import SwiftUI
import UIKit
import CoreText

/// Maryland flag palette (provisional, 2026-11-03; Nick decides, playbook/05-naming.md), light only: Calvert black #1A1A1A (17:1 on
/// white) for titles, tint and accents; Crossland red #C8102E (white on it 5.9:1) for the hand-checked guide cards under white text and
/// chips; Calvert gold #F2B705 only as a pin and card fill under dark text (gold text on white is 1.8:1, so never text on it); a warm
/// white #FAF6EC page. The flag, not team colors (Ravens and Orioles vs. Washington's teams split the state). The names `green`/`gold`
/// are kept from Wisconsin Eats so the shared views read the same; here `green` is Calvert black and `gold` is Crossland red.
enum Theme {
    static let green = Color(hex: 0x1A1A1A)      // Calvert black: titles, tint, primary text accents
    static let green2 = Color(hex: 0x3A3A3A)
    static let gold = Color(hex: 0xC8102E)       // Crossland red: card fills under white text, chips
    static let goldSoft = Color(hex: 0xF8DCE0)   // soft red
    static let lime = Color(hex: 0xF2B705)       // Calvert gold, fills only (hand-checked pins, the title shadow), under dark text
    static let limeSoft = Color(hex: 0xFCEFC4)
    static let sand = Color(hex: 0xFAF6EC)       // the Home background, warm white
    static let red = Color(hex: 0xC8102E)        // honors chips
    static let ink = Color(hex: 0x161616)
    static let ink2 = Color(hex: 0x333333)
    static let muted = Color(hex: 0x5E5E5E)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xF1EDE3)
    static let surface3 = Color(hex: 0xE6E0D2)
    static let rule = Color(hex: 0xE6E0D2)
    static let rule2 = Color(hex: 0xCFC7B5)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Maryland Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: the Calvert quarters of the flag, gold and black pales, counterchanged between the top and bottom halves.
struct Stripes: View {
    var height: CGFloat = 6

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, step = max(8, h * 0.55)
            var i = 0, x: CGFloat = 0
            while x < w {
                let top = i % 2 == 0 ? Theme.lime : Theme.green, bottom = i % 2 == 0 ? Theme.green : Theme.lime
                ctx.fill(Path(CGRect(x: x, y: 0, width: step, height: h / 2)), with: .color(top))
                ctx.fill(Path(CGRect(x: x, y: h / 2, width: step, height: h - h / 2)), with: .color(bottom))
                x += step; i += 1
            }
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
