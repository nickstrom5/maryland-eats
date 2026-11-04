import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, crabs, pitbeef, oysters, pupusas, ethiopian, korean, sweets, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // Baltimore's Inner Harbor, so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 39.2856, longitude: -76.6122)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Faidley's Seafood", "Baltimore"), pick("Thames Street Oyster House", "Baltimore"), pick("Charleston", "Baltimore")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        let silverSpring = CLLocation(latitude: 38.9907, longitude: -77.0261)
        switch name {
        case "crabs": open(.crabs)
        case "pitbeef": open(.pitBeef)
        case "oysters": open(.oysters)
        case "pupusas": model.screenshotLocation = silverSpring; open(.pupusas)
        case "ethiopian": model.screenshotLocation = silverSpring; open(.ethiopian)
        case "korean":
            // Koreatown on Route 40, Ellicott City
            model.screenshotLocation = CLLocation(latitude: 39.2850, longitude: -76.8130)
            open(.korean)
        case "sweets": open(.sweets)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Faidley's at Lexington Market: hand-checked, crab cakes since 1886, with its note
            open(.crabs)
            if let p = pick("Faidley's Seafood", "Baltimore") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("Charleston", "Baltimore")
        case "crabs": pick("Faidley's Seafood", "Baltimore")
        case "pitbeef": pick("Chaps Pit Beef", "Baltimore")
        case "oysters": pick("Thames Street Oyster House", "Baltimore")
        case "pupusas": pick("Pupuseria El Comalito", "Takoma Park")
        case "ethiopian": pick("Beteseb Restaurant", "Silver Spring")
        case "korean": pick("ChoSun Hwaro", "Ellicott City")
        case "sweets": pick("Ice Queens Snowball Shop", "Baltimore")
        case "map": pick("Faidley's Seafood", "Baltimore")
        case "honors": pick("Charleston", "Baltimore")
        case "oldest": pick("Middleton Tavern", "Annapolis")
        case "saved": pick("Thames Street Oyster House", "Baltimore")
        case "about": nil
        default: pick("Gertrude's", "Baltimore")
        }
        model.selectedPlace = place
    }
}
