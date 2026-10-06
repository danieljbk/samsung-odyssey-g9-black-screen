#!/usr/bin/env python3
"""Writes figures/outcomes.svg and figures/divider-curve.svg from the counts and the
divider values used in report.md, so a changed number is changed in one place."""

import math
from pathlib import Path

FIGURES = Path(__file__).resolve().parent / 'figures'
BLUE, ORANGE, VIOLET = '#2a78d6', '#eb6834', '#4a3aa7'
INK, MUTED, RULE = '#26262b', '#6b6b76', '#e4e4e9'

# Table 3 of report.md: fixed, not fixed, made worse or came back.
OUTCOMES = [('Original board (THA1)', 2, 1, 0),
            ('Newer board (P301)', 6, 8, 1),
            ('Board not stated', 29, 10, 2)]


def outcomes():
    left, scale, bar, gap = 150, 7.4, 22, 30
    rows = []
    for i, (label, *counts) in enumerate(OUTCOMES):
        y = 52 + i * (bar + gap)
        x = left
        unlabelled = []
        rows.append(f'<text x="{left - 10}" y="{y + 15}" text-anchor="end">{label}</text>')
        for value, colour, name in zip(counts, (BLUE, ORANGE, VIOLET), ('fixed', 'not fixed', 'worse or came back')):
            if not value:
                continue
            width = value * scale
            rows.append(f'<rect x="{x:.1f}" y="{y}" width="{width - 2:.1f}" height="{bar}" rx="3" fill="{colour}"/>')
            if width >= 20:
                rows.append(f'<text x="{x + (width - 2) / 2:.1f}" y="{y + 15}" text-anchor="middle" fill="#ffffff" font-weight="600">{value}</text>')
            else:
                # Too narrow to hold its number, so the count goes in the label after the bar.
                unlabelled.append(f'{value} {name}')
            x += width
        rows.append(f'<text x="{x + 6:.1f}" y="{y + 15}" fill="{MUTED}">{sum(counts)} posts</text>')
        if unlabelled:
            rows.append(f'<text x="{left}" y="{y + bar + 13}" fill="{MUTED}" font-size="10">{", ".join(unlabelled)}</text>')
    legend = []
    for i, (name, colour) in enumerate((('Fixed', BLUE), ('Not fixed', ORANGE), ('Made worse, or came back', VIOLET))):
        x = left + (0, 66, 156)[i]
        legend.append(f'<rect x="{x}" y="14" width="12" height="12" rx="2" fill="{colour}"/>'
                      f'<text x="{x + 18}" y="24">{name}</text>')
    svg = (f'<svg viewBox="0 0 520 196" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif" '
           f'font-size="11" fill="{INK}">' + ''.join(legend) + ''.join(rows) + '</svg>\n')
    (FIGURES / 'outcomes.svg').write_text(svg)


# The original board's divider as VINCE measured it: 3.3 V, RA13 16 kOhm in parallel with
# the thermistor, RA14 3.88 kOhm. The thermistor curve assumes 12 kOhm at 22 C and B = 3950 K.
def midpoint(celsius):
    ntc = 12000 * math.exp(3950 * (1 / (celsius + 273.15) - 1 / 295.15))
    upper = 16000 * ntc / (16000 + ntc)
    return 3.3 * 3880 / (3880 + upper)


def divider_curve():
    x0, x1, y0, y1 = 60, 500, 250, 30
    tmin, tmax, vmin, vmax = -10, 50, 0.5, 2.0
    px = lambda t: x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)
    py = lambda v: y0 - (v - vmin) / (vmax - vmin) * (y0 - y1)
    parts = []
    # trip band between 1.0 and 1.2 V
    parts.append(f'<rect x="{x0}" y="{py(1.2):.1f}" width="{x1 - x0}" height="{py(1.0) - py(1.2):.1f}" fill="#fdecd2"/>')
    parts.append(f'<text x="{x1 - 4}" y="{py(1.0) - 5:.1f}" text-anchor="end" fill="#9a5a10" font-size="9.5">the trip point on VINCE\'s monitor is in this band</text>')
    for v in (0.5, 1.0, 1.5, 2.0):
        parts.append(f'<line x1="{x0}" x2="{x1}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{RULE}"/>'
                     f'<text x="{x0 - 8}" y="{py(v) + 4:.1f}" text-anchor="end" fill="{MUTED}" font-size="10">{v:.1f} V</text>')
    for t in range(-10, 51, 10):
        parts.append(f'<text x="{px(t):.1f}" y="{y0 + 16}" text-anchor="middle" fill="{MUTED}" font-size="10">{t} °C</text>')
    parts.append(f'<text x="{(x0 + x1) / 2}" y="{y0 + 34}" text-anchor="middle" fill="{MUTED}" font-size="10">temperature the thermistor reports</text>')
    # removed line
    parts.append(f'<line x1="{x0}" x2="{x1}" y1="{py(0.644):.1f}" y2="{py(0.644):.1f}" stroke="{VIOLET}" stroke-width="2" stroke-dasharray="6 4"/>'
                 f'<text x="{x1 - 4}" y="{py(0.644) - 6:.1f}" text-anchor="end" fill="{INK}" font-size="10">thermistor removed: 0.64 V, picture</text>')
    points = ' '.join(f'{px(t / 2):.1f},{py(midpoint(t / 2)):.1f}' for t in range(-20, 101))
    parts.append(f'<polyline points="{points}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    t = 22
    parts.append(f'<circle cx="{px(t):.1f}" cy="{py(midpoint(t)):.1f}" r="5" fill="{ORANGE}" stroke="#ffffff" stroke-width="2"/>'
                 f'<text x="{px(t) - 10:.1f}" y="{py(midpoint(t)) - 10:.1f}" text-anchor="end" font-size="10">fitted, room temperature: 1.2 V, no picture</text>')
    parts.append(f'<text x="{px(46):.1f}" y="{py(midpoint(46)) - 10:.1f}" text-anchor="end" fill="{BLUE}" font-size="10" font-weight="600">midpoint voltage</text>')
    svg = (f'<svg viewBox="0 0 520 292" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif" '
           f'font-size="11" fill="{INK}">' + ''.join(parts) + '</svg>\n')
    (FIGURES / 'divider-curve.svg').write_text(svg)


if __name__ == '__main__':
    outcomes()
    divider_curve()
    print('wrote figures/outcomes.svg and figures/divider-curve.svg')
