// Maryland Eats brand (provisional, 2026-11-03; Nick picks the name, icon and palette): the app icon is concept A of
// scripts/icon-concepts.swift, a steamed crab with gold seasoning flecks, on Calvert black; the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No Great Seal, no Old Bay tin, no team marks.
// Usage, from md-eats/: swift scripts/make-brand.swift   -> MarylandEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let BLACK: UInt32 = 0x1A1A1A, ORANGE: UInt32 = 0xD9532B, RED: UInt32 = 0xC8102E, GOLD: UInt32 = 0xF2B705

/// The steamed crab. CoreGraphics y-up, s = canvas size. Identical to icon-concepts.swift's concept A.
func crab(_ c: CGContext, _ s: CGFloat) {
    func P(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }
    c.setLineCap(.round); c.setLineJoin(.round)
    // three walking legs a side, thick round strokes swept down and out
    c.setStrokeColor(rgb(ORANGE)); c.setLineWidth(0.042 * s)
    for (y0, x1, y1) in [(0.47, 0.165, 0.43), (0.42, 0.18, 0.345), (0.375, 0.225, 0.27)] as [(CGFloat, CGFloat, CGFloat)] {
        c.move(to: P(0.40, y0)); c.addLine(to: P(x1, y1)); c.strokePath()
        c.move(to: P(0.60, y0)); c.addLine(to: P(1 - x1, y1)); c.strokePath()
    }
    // the claw arms, up and out from the shell's front
    c.setLineWidth(0.05 * s)
    c.move(to: P(0.40, 0.58)); c.addLine(to: P(0.30, 0.67)); c.strokePath()
    c.move(to: P(0.60, 0.58)); c.addLine(to: P(0.70, 0.67)); c.strokePath()
    // the claws: orange palms with red tips
    for x in [0.255, 0.745] as [CGFloat] {
        c.setFillColor(rgb(ORANGE)); c.fillEllipse(in: CGRect(x: (x - 0.075) * s, y: 0.63 * s, width: 0.15 * s, height: 0.12 * s))
        c.setFillColor(rgb(RED)); c.fillEllipse(in: CGRect(x: (x - 0.05) * s, y: 0.70 * s, width: 0.10 * s, height: 0.075 * s))
    }
    // the shell: a wide oval, and a red seam along its front edge
    c.setFillColor(rgb(RED)); c.fillEllipse(in: CGRect(x: 0.255 * s, y: 0.335 * s, width: 0.49 * s, height: 0.30 * s))
    c.setFillColor(rgb(ORANGE)); c.fillEllipse(in: CGRect(x: 0.255 * s, y: 0.35 * s, width: 0.49 * s, height: 0.285 * s))
    // the seasoning: six gold flecks on the shell
    c.setFillColor(rgb(GOLD))
    for (x, y) in [(0.37, 0.52), (0.46, 0.565), (0.56, 0.535), (0.63, 0.47), (0.42, 0.44), (0.53, 0.43)] as [(CGFloat, CGFloat)] {
        c.fillEllipse(in: CGRect(x: (x - 0.022) * s, y: (y - 0.022) * s, width: 0.044 * s, height: 0.044 * s))
    }
}


func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(BLACK)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    crab(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "MarylandEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): Calvert black, the crab at the left, the name and tagline at the right, and the app's header band
/// along the bottom: the flag's Calvert gold and black pales, counterchanged.
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(BLACK)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    var x: CGFloat = 0, i = 0
    while x < CGFloat(W) {
        ctx.setFillColor(rgb(i % 2 == 0 ? GOLD : BLACK)); ctx.fill(CGRect(x: x, y: 22, width: 30, height: 22))
        ctx.setFillColor(rgb(i % 2 == 0 ? BLACK : GOLD)); ctx.fill(CGRect(x: x, y: 0, width: 30, height: 22))
        x += 30; i += 1
    }
    ctx.saveGState(); ctx.translateBy(x: 30, y: 80); crab(ctx, 500); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 96) ?? NSFont.boldSystemFont(ofSize: 84)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 38) ?? NSFont.boldSystemFont(ofSize: 34)
    NSAttributedString(string: "MARYLAND EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 580, y: 330))
    NSAttributedString(string: "CRAB CAKES, PIT BEEF & OYSTERS", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.949, green: 0.718, blue: 0.020, alpha: 1)]).draw(at: NSPoint(x: 584, y: 272))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
