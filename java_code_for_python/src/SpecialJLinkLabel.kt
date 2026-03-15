/*
 * Copyright (c) 2020-2026 Stuart Beesley - StuWareSoftSystems
 * Moneydance components Copyright (c) 1999-2026 The Infinite Kind, Limited
 */

import com.moneydance.apps.md.view.gui.MDColors
import com.moneydance.awt.JLinkLabel
import java.awt.*
import java.awt.geom.Path2D
import javax.swing.JLabel
import javax.swing.SwingUtilities
import kotlin.math.max
import kotlin.math.min

@Suppress("UNUSED")

/**
 * A JLinkLabel subclass that draws a dotted underline in the space between the label text
 * and the edge of the component, and enforces stable preferred size accumulation to prevent
 * column width jitter during widget rebuilds.
 *
 * Implemented in Kotlin (rather than Jython) to avoid the Jython bridge penalty on
 * paintComponent() which causes macOS to use heavyweight compositing and spawn CVDisplayLink
 * threads for every visible instance.
 */
class SpecialJLinkLabel : JLinkLabel {

    var underlineDots = false
    var allowDynamicSizing = false
    private var maxWidth = -1
    private var maxHeight = -1
    private val underlineStroke: BasicStroke

    constructor(text: String?, linkTarget: Any?, alignment: Int)
            : super(text, linkTarget, alignment) {
        this.underlineStroke = makeStroke(alignment)
    }

    constructor(text: String?, linkTarget: Any?, alignment: Int, underlineDots: Boolean, allowDynamicSizing: Boolean = false)
            : super(text, linkTarget, alignment) {
        this.underlineDots = underlineDots
        this.allowDynamicSizing = allowDynamicSizing
        this.underlineStroke = makeStroke(alignment)
    }

    private fun makeStroke(alignment: Int): BasicStroke {
        val phase = if (alignment == JLabel.LEFT) 1.0f else 0.0f
        return BasicStroke(1.0f, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL, 1.0f, floatArrayOf(1.0f, 6.0f), phase)
    }

    override fun getPreferredSize(): Dimension {
        val dim = super.getPreferredSize()
        return if (allowDynamicSizing) {
            dim.also { it.width = min(200, it.width) }
        } else {
            maxWidth = max(maxWidth, dim.width)
            maxHeight = max(maxHeight, dim.height)
            Dimension(maxWidth, maxHeight)
        }
    }

    override fun paintComponent(g: Graphics) {
        super.paintComponent(g)
        if (!underlineDots) return
        val g2d = g as? Graphics2D ?: return

        val isLeftAlign = (horizontalAlignment == JLabel.LEFT)
        val w = width
        val h = height
        val insets = insets

        val viewR = Rectangle(w, h)
        val iconR = Rectangle()
        val textR = Rectangle()

        SwingUtilities.layoutCompoundLabel(
            this,
            g2d.fontMetrics,
            text,
            icon,
            verticalAlignment,
            horizontalAlignment,
            verticalTextPosition,
            horizontalTextPosition,
            viewR,
            iconR,
            textR,
            iconTextGap
        )

        val visibleTextWidth = textR.width

        val maxBaseline = g2d.fontMetrics.maxDescent
        val baselineY = (h - maxBaseline - 1).toDouble()

        val startDots: Int
        val lengthOfDots: Int
        if (isLeftAlign) {
            startDots = visibleTextWidth + insets.left
            lengthOfDots = w - startDots
        } else {
            startDots = 0
            lengthOfDots = w - visibleTextWidth - insets.right
        }

        val line = Path2D.Double()
        line.moveTo(if (isLeftAlign) w.toDouble() else 0.0, baselineY - insets.top)
        line.lineTo(if (isLeftAlign) 0.0 else w.toDouble(), baselineY - insets.top)

        val savedClip = g2d.clip
        g2d.color = MDColors.getSingleton().defaultTextForeground
        g2d.clipRect(startDots, 0, lengthOfDots, h)
        g2d.stroke = underlineStroke
        g2d.draw(line)
        g2d.clip = savedClip
    }
}