import SwiftUI

struct AboutView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("MARYLAND EATS").displayFont(32).foregroundStyle(Theme.green)
                    Text("A free guide to \(model.restaurantCount.formatted()) Maryland restaurants, with James Beard honors, Montgomery County's inspection results, county license lists, and hand-checked lists of Maryland's own food: crab cakes and crab houses, pit beef, oyster bars, pupuserías, Ethiopian, Route 40 Korean and snowballs. No account, no ads, no tracking.")
                        .font(.subheadline).foregroundStyle(Theme.ink2)
                    Text("Maryland Eats is an independent app by Nicholas Soderstrom. It is not affiliated with, endorsed by or operated by the State of Maryland, the Maryland Department of Health, any county or Baltimore City, their health departments or liquor boards, Visit Maryland or any county tourism office, the James Beard Foundation, Apple, or any restaurant or chain. Other names are trademarks of their owners.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                .padding(.vertical, 4)
            }
            Section("How the lists are built") {
                Text("Hand-checked lists (crab cakes and crab houses, pit beef, oyster bars, pupuserías, Ethiopian, Route 40 Korean, snowball stands and the oldest places) include only places checked against a 2025 or 2026 source (a dated magazine or news story or an official tourism listing), with the address checked. Founding years mean the year it opened at this address.")
                Text("Honors are James Beard Foundation winners, finalists and semifinalists. There is no MICHELIN Guide for Maryland: its Washington, DC selection stops at the District line.")
                Text("Maryland publishes no open list of its restaurants statewide. This app starts from open map listings (Overture Maps) and keeps the kinds that proved reliable: checked against the food facilities Montgomery and Anne Arundel counties inspect, high-confidence listings matched far more often than the kinds left out. Those lists, and Baltimore City's liquor licenses, also confirm places and add inspected restaurants the map data missed. Montgomery County's and Baltimore City's alcohol licenses say which places there serve drinks; anywhere else that's unknown, never no. Adult clubs are left out, and stadium, airport and campus stands are hidden with the non-restaurants. Website links are checked, and any that no longer belong to the place are left out.")
                Text("Each of Maryland's 24 local health departments inspects its own restaurants. Montgomery County publishes every inspection with its result (Pass, Fail, Closed), so those places show the county's latest result and date, as the county words it; this app computes no grade. Elsewhere results aren't published as data, and each place links to the list of health departments.")
                Text("Ratings, reviews, hours and photos are Apple Maps' own, shown live in Apple's place card. This app doesn't store or rank by them.")
            }
            .font(.subheadline).foregroundStyle(Theme.ink2)
            Section("Sources") {
                source("Montgomery County, Maryland", "HHS Food Inspection Data from July 2024 onward and Alcohol Beverage Services Licensee Data (data.montgomerycountymd.gov), public domain, updated daily and monthly, as of \(model.permitsUpdated); modified for use in this app. Owner and licensee names are never used.", Links.licenses.absoluteString)
                source("Anne Arundel County Department of Health", "Restaurant Inspection Dataset (opendata.aacounty.org), 2025 to 2026: which facilities are inspected. Modified for use in this app.", "https://opendata.aacounty.org/datasets/e540546f30854288a5279898946f5ba2")
                source("Baltimore City", "Liquor licenses (CityView Licenses, CC BY 3.0), the 2026 licenses by trade name and class; licensee names are never used. Modified for use in this app.", "https://baltegis.baltimorecity.gov/mapping/rest/services/CityView/Licenses/FeatureServer/0")
                source("Maryland Department of Health", "The list of local health departments, each with its own food program. Linked from each place.", Links.inspections.absoluteString)
                source("Overture Maps Foundation", "Restaurant listings and websites come from Overture Maps Foundation places data (overturemaps.org)\(model.overtureRelease.map { ", release \($0)" } ?? ""), filtered and reformatted for this app.\n• Data from Meta, Microsoft, DAC and BrightQuery. Available under CDLA Permissive 2.0.\n• Data from Foursquare. \(foursquareCopyright) Available under Apache 2.0. Foursquare data was transformed to the Overture schema; this app further filtered and reformatted it. See the NOTICE below.\n• Data from AllThePlaces. Available under CC0 1.0.\nResearched places are put on the map with Overture Maps addresses data (open address sources under permissive licenses, docs.overturemaps.org/attribution).", "https://overturemaps.org")
                source("Honors", "James Beard Foundation awards are reported as facts and checked by hand against the official announcements. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Other names belong to their owners.", "https://www.jamesbeard.org/awards")
                source("Maps", "Maps, place cards and directions by Apple Maps.", nil)
            }
            Section("Licenses") {
                NavigationLink("Community Data License Agreement – Permissive 2.0") { LicenseText(file: "CDLA-Permissive-2.0", title: "CDLA Permissive 2.0") }
                NavigationLink("Apache License 2.0") { LicenseText(file: "Apache-2.0", title: "Apache License 2.0") }
                NavigationLink("Foursquare OS Places NOTICE") { LicenseText(file: "Foursquare-NOTICE", title: "Foursquare NOTICE") }
            }
            Section("Privacy") {
                Text("The app collects nothing. Your location, if you allow it, only sorts lists by distance and shows where you are on the map, on this device. Saved places stay on this device.")
                    .font(.subheadline).foregroundStyle(Theme.ink2)
                DataUpdatesNote()
                    .font(.footnote).foregroundStyle(Theme.muted)
                Link("Privacy policy", destination: Links.privacy)
                Link("Terms of use", destination: Links.terms)
            }
            Section("Help") {
                Link("Report a missing or closed place", destination: Links.correctionEmail)
                Link("Email \(Links.supportEmail)", destination: URL(string: "mailto:\(Links.supportEmail)")!)
                Link("Website", destination: Links.site)
                Text("Data as of \(DayFormat.text(model.generated) ?? model.generated). Places open and close; check before you go. Version \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0")")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("About")
        .tint(Theme.green)
    }

    /// the copyright line exactly as the bundled Foursquare NOTICE has it, so the two can't disagree
    private var foursquareCopyright: String {
        guard let url = Bundle.main.url(forResource: "Foursquare-NOTICE", withExtension: "txt"),
              let text = try? String(contentsOf: url, encoding: .utf8),
              let line = text.split(separator: "\n").first(where: { $0.hasPrefix("©") }) else { return "© Foursquare Labs, Inc. All rights reserved." }
        return line.trimmingCharacters(in: .whitespaces)
    }

    @ViewBuilder
    private func source(_ name: String, _ detail: String, _ url: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let url, let u = URL(string: url) { Link(name, destination: u).font(.subheadline.weight(.semibold)) }
            else { Text(name).font(.subheadline.weight(.semibold)) }
            Text(detail).font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

/// A bundled license text (Resources/Licenses), reflowed rather than shown as raw 80-column lines.
struct LicenseText: View {
    let file: String
    let title: String

    var body: some View {
        ScrollView {
            Text(text).font(.footnote).foregroundStyle(Theme.ink).textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading).padding()
        }
        .inlineTitle(title)
    }

    private var text: String {
        guard let url = Bundle.main.url(forResource: file, withExtension: "txt"),
              let raw = try? String(contentsOf: url, encoding: .utf8) else { return "License text missing." }
        // join hard-wrapped lines into paragraphs; keep blank lines and list items as breaks
        var out: [String] = []
        for para in raw.components(separatedBy: "\n\n") {
            let lines = para.components(separatedBy: "\n").map { $0.trimmingCharacters(in: .whitespaces) }
            var joined = ""
            for l in lines where !l.isEmpty {
                let startsItem = l.hasPrefix("–") || l.hasPrefix("-") || l.range(of: #"^\(?[a-z0-9]{1,3}[.)]\s"#, options: .regularExpression) != nil
                joined += joined.isEmpty ? l : (startsItem ? "\n" + l : " " + l)
            }
            if !joined.isEmpty { out.append(joined) }
        }
        return out.joined(separator: "\n\n")
    }
}
