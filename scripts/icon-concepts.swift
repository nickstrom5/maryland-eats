// Maryland Eats icon concepts (2026-11-03), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on Calvert black #1A1A1A, no backing shape, no text or texture. Food hexes: Chesapeake crab orange #D9532B, Crossland
// red #C8102E, Calvert gold #F2B705 (the prompt's palettes).
//   A  a steamed crab seen from above (round, so a plan view is allowed): orange shell, red claw tips, six gold seasoning flecks
//   B  a slice of Smith Island cake, the state dessert: thin gold layers between chocolate icing, front view
//   C  a Baltimore snowball: a white cup with a red shaved-ice dome and a marshmallow cap
// Usage, from md-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let BLACK: UInt32 = 0x1A1A1A, ORANGE: UInt32 = 0xD9532B, RED: UInt32 = 0xC8102E, GOLD: UInt32 = 0xF2B705

/// A: the steamed crab. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's crab().
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

/// B: a slice of Smith Island cake, front view: eight thin gold layers between chocolate icing, a chocolate top.
func cake(_ c: CGContext, _ s: CGFloat) {
    let CHOC: UInt32 = 0x4A2C1A, CHOC2: UInt32 = 0x6B4127
    let x0 = 0.145 * s, w = 0.71 * s, y0 = 0.26 * s, h = 0.40 * s
    c.setFillColor(rgb(CHOC)); c.fill(CGRect(x: x0, y: y0, width: w, height: h))
    let n = 6, band = h / CGFloat(2 * n + 1)
    c.setFillColor(rgb(GOLD))
    for i in 0..<n { c.fill(CGRect(x: x0, y: y0 + band * CGFloat(2 * i + 1), width: w, height: band)) }
    c.setFillColor(rgb(CHOC2)); c.fill(CGRect(x: x0, y: y0 + h, width: w, height: 0.07 * s))
}

/// C: a Baltimore snowball: a white cup, a red dome of shaved ice, a marshmallow cap.
func snowball(_ c: CGContext, _ s: CGFloat) {
    func P(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }
    let cup = CGMutablePath()
    cup.move(to: P(0.29, 0.50)); cup.addLine(to: P(0.71, 0.50)); cup.addLine(to: P(0.635, 0.135)); cup.addLine(to: P(0.365, 0.135)); cup.closeSubpath()
    c.setFillColor(rgb(0xF7F3EA)); c.addPath(cup); c.fillPath()
    c.setFillColor(rgb(RED)); c.fillEllipse(in: CGRect(x: 0.26 * s, y: 0.38 * s, width: 0.48 * s, height: 0.42 * s))
    c.setFillColor(rgb(0xF7F3EA)); c.fillEllipse(in: CGRect(x: 0.355 * s, y: 0.69 * s, width: 0.29 * s, height: 0.155 * s))
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(BLACK)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", crab)
render(1024, out + "/concept-b-1024.png", cake)
render(1024, out + "/concept-c-1024.png", snowball)
