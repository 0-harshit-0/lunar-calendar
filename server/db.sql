CREATE TABLE lunar_ephemeris (
    date DATE PRIMARY KEY,

    ayana VARCHAR(32) NOT NULL,
    ritu VARCHAR(32) NOT NULL,
    masa VARCHAR(32) NOT NULL,
    paksha VARCHAR(32) NOT NULL,
    tithi VARCHAR(32) NOT NULL,
    phase VARCHAR(16) NOT NULL,

    surya_rashi VARCHAR(32) NOT NULL,
    chandra_rashi VARCHAR(32) NOT NULL,

    surya_longitude_deg DOUBLE NOT NULL,
    chandra_longitude_deg DOUBLE NOT NULL,
    longitudinal_angle_deg DOUBLE NOT NULL,

    surya_xyz JSON NOT NULL,
    chandra_xyz JSON NOT NULL,

    fasting_days JSON NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
