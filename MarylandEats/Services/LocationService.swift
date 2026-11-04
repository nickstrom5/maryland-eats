import CoreLocation
import Observation
import UIKit

/// "Near me" sorting. Asks for when-in-use permission only when a list is sorted by distance or "My location" is tapped; the location never leaves the device.
@MainActor
@Observable
final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private(set) var location: CLLocation?
    private(set) var status: CLAuthorizationStatus = .notDetermined
    /// no fix within 12 seconds, or Core Location reported an error
    private(set) var failed = false
    private var timeout: Task<Void, Never>?
    /// when the current request started: a fix from before it is a cached one (from launch, or before a drive) and doesn't count
    private var askedAt = Date.distantPast

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        status = manager.authorizationStatus
    }

    var isDenied: Bool { status == .denied || status == .restricted }

    /// Every place is in Maryland, so a reader elsewhere (an App Reviewer in California, say) gets told rather than an empty map.
    /// A coarse outline of the state (Idaho's lesson: a bounding box would count Wilmington, York and Arlington), drawn a little outside
    /// the line so Ocean City, Assateague, Smith Island and Point Lookout count as inside.
    var isOutsideMaryland: Bool {
        guard let c = location?.coordinate else { return false }
        return !MarylandOutline.contains(c)
    }

    /// Once location is off for the app, iOS won't ask again; the app's page in Settings is the only way back.
    static func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
    }

    func request() {
        switch manager.authorizationStatus {
        case .notDetermined: manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways: locate()
        default: break
        }
    }

    private func locate() {
        failed = false
        let asked = Date()
        askedAt = asked
        manager.requestLocation()
        timeout?.cancel()
        timeout = Task { [weak self] in
            try? await Task.sleep(for: .seconds(12))
            guard let self, !Task.isCancelled else { return }
            if (self.location?.timestamp ?? .distantPast) < asked { self.failed = true }
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let s = m.authorizationStatus
        Task { @MainActor in
            self.status = s
            if s == .authorizedWhenInUse || s == .authorizedAlways { self.locate() }
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let l = locations.last else { return }
        Task { @MainActor in
            // "My location" needs a fresh fix on every tap: a cached one from before the request would put you back where you were
            guard l.timestamp >= self.askedAt.addingTimeInterval(-2) else { return }
            self.location = l; self.failed = false; self.timeout?.cancel()
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in if self.location == nil { self.failed = true } }
    }
}

extension CLLocation {
    /// "0.4 mi", "12 mi", "1,012 mi" (an App Reviewer in California is a thousand miles out)
    func milesText(to other: CLLocation) -> String {
        let mi = distance(from: other) / 1609.344
        return (mi < 10 ? mi.formatted(.number.precision(.fractionLength(1))) : Int(mi.rounded()).formatted()) + " mi"
    }
}

/// A coarse Maryland outline (longitude, latitude): the state (41 points) and a small ring at its edge, about 4 km outside the
/// Overture land outline (buffer 0.04°, simplify 0.05°), Smith Island, Tilghman, Solomons and Assateague included. Baltimore, Ocean City,
/// Oakland and Elkton are inside; Wilmington, Dover, York, Harrisburg, Arlington, Martinsburg and Washington, DC are not (Alexandria's
/// riverfront falls in the margin across the Potomac).
enum MarylandOutline {
    static let rings: [[(Double, Double)]] = [
        [(-79.53, 39.26), (-79.48, 39.76), (-75.78, 39.76), (-75.66, 38.50), (-75.05, 38.49), (-75.01, 38.43), (-75.22, 37.99),
         (-75.89, 37.87), (-75.92, 38.08), (-75.97, 38.08), (-75.95, 37.94), (-76.06, 37.92), (-76.13, 38.20), (-76.37, 38.46),
         (-76.32, 38.64), (-76.43, 38.76), (-76.40, 38.96), (-76.50, 38.76), (-76.48, 38.55), (-76.34, 38.40), (-76.28, 38.03),
         (-76.49, 38.06), (-76.49, 37.98), (-76.62, 38.08), (-76.61, 38.18), (-76.79, 38.19), (-76.85, 38.12), (-76.98, 38.18),
         (-77.06, 38.34), (-77.31, 38.32), (-77.35, 38.51), (-76.97, 38.89), (-77.48, 39.04), (-77.57, 39.13), (-77.53, 39.22),
         (-77.78, 39.30), (-77.93, 39.55), (-78.12, 39.64), (-78.46, 39.48), (-78.78, 39.55), (-79.46, 39.16)],
        [(-76.20, 37.88), (-76.29, 37.91), (-76.24, 37.94)]]

    static func contains(_ c: CLLocationCoordinate2D) -> Bool { rings.contains { contains(c, ring: $0) } }

    /// Ray casting: a point is inside when a ray east of it crosses the outline an odd number of times.
    static func contains(_ c: CLLocationCoordinate2D, ring: [(Double, Double)]) -> Bool {
        var inside = false
        var j = ring.count - 1
        for i in 0..<ring.count {
            let (xi, yi) = ring[i], (xj, yj) = ring[j]
            if (yi > c.latitude) != (yj > c.latitude) && c.longitude < (xj - xi) * (c.latitude - yi) / (yj - yi) + xi { inside.toggle() }
            j = i
        }
        return inside
    }
}
