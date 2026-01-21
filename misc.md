# Lat and Long
Latitude by itself tells you how far north or south a point is from the equator. On a flat or purely 2D view, all points on the same horizontal line look equivalent.

Longitude only makes sense when you consider the Earth as a 3D sphere with a center. Longitudes are angles around the Earth’s axis, measured from the prime meridian at the center of the Earth. Without the 3D perspective, longitude has no physical meaning because there is no rotation or central reference.

In short:

Latitude is a north–south angle and can be understood in 2D.

Longitude is an east–west angle around the Earth’s axis and requires a 3D spherical view.

A full geographic position only exists when you think in 3D angles from the Earth’s center.

# WHY NOT TAN or SIN or COS
When distance would matter

Distance matters only if you were computing:

apparent angular diameter

parallax

shadow geometry

eclipse cone intersections

But not for longitude or phase angle.

Intuitive check

Imagine shrinking the Sun’s distance until it is as close as the Moon.

The longitudinal angle would not change at all.

That alone proves distance is irrelevant.

One-sentence conclusion

The longitudinal angle is a directional angle, so it must be computed from vector directions using atan2, not from distances using tan.

# WHY NOT DOT PRODUCT OVER MAG
Comparison summary
Method  What it gives Direction?
atan2 longitude Pure longitude difference Yes
Dot product (XY only) Absolute longitude separation No
Dot product (XYZ) True 3D angular separation  No
Practical rule

For tithi, phase, waxing/waning → use atan2 longitude

For angular separation or eclipse geometry → use 3D dot product

For just “how far apart in longitude” (unsigned) → XY dot product is fine

One-sentence takeaway

The dot product is valid, but full 3D gives elongation, while projected dot product gives unsigned longitude, and only atan2 gives signed longitudinal angle, which is why it is preferred.

# Waxing

Waxing means:

the illuminated portion of the Moon is increasing day by day.

Geometrically:

The Moon is moving eastward ahead of the Sun in longitude

The Moon’s longitude is greater than the Sun’s longitude

The longitudinal angle (Moon − Sun) is positive and increasing

Examples:

New Moon → Waxing Crescent → First Quarter → Waxing Gibbous → Full Moon

# Waning

Waning means:

the illuminated portion of the Moon is decreasing day by day.

Geometrically:

The Moon is behind the Sun in longitude

The Moon’s longitude is less than the Sun’s longitude

The longitudinal angle (Moon − Sun) is negative or decreasing

Examples:

Full Moon → Waning Gibbous → Last Quarter → Waning Crescent → New Moon

Why longitude determines waxing or waning

The Moon always orbits eastward around Earth faster than the Sun appears to move.

So:

When the Moon is catching up to the Sun from behind, illumination shrinks → waning

When the Moon has passed the Sun, illumination grows → waxing

This is why the sign of the longitudinal difference matters.
      -->
