"""Official NCCT catalogue families (https://ncctdxb.com/en/Real/*.html) not imported by catalogue-v1.

Names and descriptions only describe what the published catalogue image visibly shows. No model numbers,
ratings or technical specifications are invented. Images with visible third-party brand marks are imported
as unpublished drafts for the client to approve.
"""
BASE = 'https://ncctdxb.com/en/Real/'

# key, name, description, source page, hero image, alt text
CATEGORIES = [
    ('led', 'LED lighting', 'Contemporary LED luminaires: ring, linear, hexagon and colour-changing forms.', 'Led_lights.html', 'led_p6', 'Gold LED ring ceiling luminaire'),
    ('control', 'Control gear', 'Drivers, controllers and power supplies for LED lighting systems.', 'Control_Gears.html', 'cont_p3', 'LED driver and power supply units'),
    ('lamps', 'Lamps', 'Table and portable lamps for living, working and hospitality settings.', 'Lamps.html', 'lamp_p1', 'Spiral LED table lamp'),
    ('emergency', 'Emergency lighting', 'Emergency luminaires and exit signage.', 'Emergency.html', 'emer_p5', 'Twin-head emergency luminaire'),
]
LEGACY = {'led': 'Led_lights', 'control': 'Control_Gears', 'lamps': 'Lamps', 'emergency': 'Emergency'}

# code, category key, name, description, mounting type, published
PRODUCTS = [
    ('ind_p2', 'indoor', 'Slim round surface ceiling light', 'A slim white round LED-style surface ceiling light with a diffused face.', 'Surface ceiling', True),
    ('ind_p4', 'indoor', 'Chrome wall light with pull cord', 'A chrome wall light with an opal cylindrical shade and pull-cord switch.', 'Wall', True),
    ('ind_p5', 'indoor', 'Aluminium up-and-down wall light', 'A brushed aluminium wall light that projects light upwards and downwards.', 'Wall', True),
    ('ind_p6', 'indoor', 'Woven rattan pendant lights', 'Spherical woven rattan pendant lights for warm, textured interiors.', 'Pendant', True),
    ('ind_p7', 'indoor', 'Brass globe wall light', 'A brass wall light with a curved arm and opal glass globe.', 'Wall', True),
    ('out_p1', 'outdoor', 'Oval bulkhead light', 'A black oval bulkhead light with a ribbed frosted diffuser and protective cage.', 'Wall or ceiling', True),
    ('out_p2', 'outdoor', 'Square framed wall light', 'A square black-framed outdoor wall light with a frosted diffuser.', 'Wall', True),
    ('out_p3', 'outdoor', 'Traditional post lantern', 'A black traditional lantern with clear glass panels, shown on a gate post.', 'Post', True),
    ('out_p4', 'outdoor', 'Contemporary lantern wall light', 'A black outdoor wall lantern with a frosted glass body and linear frame.', 'Wall', True),
    ('out_p5', 'outdoor', 'Barn-style gooseneck wall light', 'A black barn-style wall light with a gooseneck arm and caged glass shade.', 'Wall', True),
    ('out_p6', 'outdoor', 'Up-and-down outdoor wall light', 'A slim black outdoor wall light that casts light upwards and downwards.', 'Wall', True),
    ('out_p7', 'outdoor', 'Pagoda-style garden lantern', 'A black pagoda-style garden lantern with a warm glowing body.', 'Post or table', True),
    ('deco_p1', 'decorative', 'LED icicle curtain lights', 'A cascading warm-white icicle string light along a roofline.', 'String', True),
    ('deco_p2', 'decorative', 'Copper wire fairy lights', 'A warm-white string of micro lights on flexible copper wire.', 'String', True),
    ('deco_p3', 'decorative', 'Firework burst string lights', 'Burst-shaped warm-white decorative string lights.', 'Hanging', True),
    ('deco_p4', 'decorative', 'Star curtain lights', 'Warm-white star-shaped curtain lights for windows and soft furnishings.', 'Hanging', True),
    ('deco_p5', 'decorative', 'Wall-mounted pattern projection lights', 'Small wall lights that cast a decorative radial pattern.', 'Wall', True),
    ('deco_p6', 'decorative', 'Petal-form bamboo pendant', 'A hanging pendant with layered bamboo petals.', 'Pendant', True),
    ('deco_p7', 'decorative', 'Backlit wooden wall panel', 'A faceted wooden feature wall with concealed warm LED edge lighting.', 'Wall feature', True),
    ('indus_p2', 'industrial', 'Four-spot ceiling track light', 'A black ceiling rail with four adjustable spot heads.', 'Ceiling', True),
    ('indus_p3', 'industrial', 'Twin retro spot ceiling light', 'A black twin-head ceiling light with adjustable retro spot shades.', 'Ceiling', True),
    ('indus_p4', 'industrial', 'Caged dome semi-flush light', 'A rust-finish semi-flush ceiling light with a dome shade and wire cage.', 'Semi-flush ceiling', True),
    ('indus_p5', 'industrial', 'Mesh cylinder pendant pair', 'A pair of black mesh cylinder pendants with filament-style lamps.', 'Pendant', True),
    ('indus_p6', 'industrial', 'Theatre-style barn door spot', 'A black theatre-style ceiling spot with barn doors.', 'Ceiling', True),
    ('indus_p8', 'industrial', 'Three-light glass globe vanity light', 'A black bar wall light with three clear glass globe shades.', 'Wall', True),
    ('prof_p1', 'professional', 'RGB panel light kit with stands', 'A pair of panel lights with barn doors, stands and app control. The image shows a third-party brand mark.', 'Stand', False),
    ('prof_p2', 'professional', 'LED panel light pair with stands', 'A pair of LED panel lights with barn doors on adjustable stands.', 'Stand', True),
    ('prof_p3', 'professional', 'COB LED par light', 'A black par-style fixture with a COB LED source and reflector.', 'Floor or truss', True),
    ('prof_p4', 'professional', 'LED soft panel with barn doors', 'A rectangular LED panel with barn doors and a yoke for hanging or stand mounting.', 'Yoke', True),
    ('prof_p5', 'professional', 'Gobo track spotlight', 'A black track-mounted spotlight with a focusing barrel and interchangeable gobo wheel.', 'Track', True),
    ('prof_p6', 'professional', 'Softbox lighting kit', 'A pair of rectangular softboxes on stands.', 'Stand', True),
    ('prof_p7', 'professional', 'Octagonal softbox studio light', 'An octagonal softbox with a studio light head. The image shows a third-party brand mark.', 'Stand', False),
    ('prof_p8', 'professional', 'Barn door panel on tall stand', 'A black LED panel with barn doors on a tall stand, shown in a living room.', 'Stand', True),
    ('prof_p9', 'professional', 'Studio LED light with reflector', 'A studio LED head with a bowl reflector and control display. The image shows a third-party brand mark.', 'Stand', False),
    ('led_p1', 'led', 'LED garden path lights', 'Slim LED garden path lights casting patterned light across paving.', 'Ground spike', True),
    ('led_p2', 'led', 'RGB LED ring wall light', 'A circular wall-mounted LED ring with a colour-changing glow.', 'Wall', True),
    ('led_p3', 'led', 'Square-module LED ceiling light', 'A black ceiling light with three linked square LED modules.', 'Ceiling', True),
    ('led_p4', 'led', 'Hexagon LED ceiling grid', 'A modular honeycomb LED ceiling light for workshops and showrooms.', 'Ceiling', True),
    ('led_p5', 'led', 'Twin linear LED wall light', 'Two offset vertical LED bars on a gold backplate.', 'Wall', True),
    ('led_p6', 'led', 'Gold ring LED ceiling light', 'A multi-ring ceiling light with gold finish and warm LED rings.', 'Ceiling', True),
    ('cont_p1', 'control', 'Wireless lighting control unit', 'A wireless lighting controller with an external antenna. The image shows a third-party brand mark.', 'Surface', False),
    ('cont_p2', 'control', 'Emergency LED conversion module', 'A compact module with terminal block for LED emergency applications.', 'Concealed', True),
    ('cont_p3', 'control', 'Waterproof LED power supply and driver', 'A metal-cased LED power supply with a separate small driver unit.', 'Surface', True),
    ('cont_p4', 'control', 'Linear LED driver', 'A slim linear LED driver with screw terminals. The image shows a third-party brand mark.', 'Concealed', False),
    ('lamp_p1', 'lamps', 'Spiral LED table lamp', 'A sculptural spiral LED table lamp with a dark base.', 'Table', True),
    ('lamp_p2', 'lamps', 'Crescent moon table lamp', 'A gold crescent-shaped table lamp holding a glowing fairy-light globe.', 'Table', True),
    ('lamp_p3', 'lamps', 'Flexible-neck desk lamp', 'A black desk lamp with a flexible neck and cone shade.', 'Desk', True),
    ('lamp_p4', 'lamps', 'Rattan-shade portable table lamp', 'A cordless-style table lamp with a woven rattan shade for patios and dining.', 'Table', True),
    ('emer_p1', 'emergency', 'Twin-head emergency light unit', 'A twin-head emergency light with a battery housing and status panel.', 'Wall', True),
    ('emer_p2', 'emergency', 'Exit sign with emergency heads', 'An illuminated EXIT sign with two integrated emergency lamp heads.', 'Wall or ceiling', True),
    ('emer_p3', 'emergency', 'Wet-location twin-head emergency light', 'A twin-head emergency light with a sealed grey housing.', 'Wall', True),
    ('emer_p4', 'emergency', 'Twin-lamp emergency light', 'A white emergency light with two adjustable lamp heads.', 'Wall', True),
    ('emer_p5', 'emergency', 'Twin LED emergency light', 'A white emergency light with two adjustable square LED heads.', 'Wall', True),
]

APPLICATION_BY_CATEGORY = {'indoor': 'indoor', 'outdoor': 'outdoor', 'decorative': 'decorative', 'industrial': 'industrial', 'professional': 'professional'}

# Reference scenes: NCCT website imagery, shown as illustrative lighting references, not delivered projects.
PROJECT_REFERENCES = [
    ('The architecture of atmosphere', 'Residential interior', 'homepg-4', 'Open-plan interior with concealed cove lighting, pendants and display-shelf illumination',
     'Layered ambient, accent and display lighting in a contemporary open-plan interior. Warm cove light defines the ceiling plane, while shelves and joinery are lit to bring depth to the room.',
     ['homepg-5', 'homepg-6']),
    ('A path, quietly defined', 'Landscape & pathways', 'homepg-2', 'Curving garden path with warm edge lighting',
     'Low-level linear light traces a sweeping path and step edges, guiding movement after dark while keeping the garden calm and uncluttered.',
     ['pg-2', 'pg-1']),
    ('After the sun goes down', 'Outdoor entertaining', 'homepg-3', 'Terraced garden with lit planters, steps and dining area',
     'Integrated lighting extends outdoor living into the evening: lit planter edges, steps and accent lighting create safe, inviting terraces.',
     ['homepg-1']),
    ('Lit stair and dining', 'Residential interior', 'homepg-5', 'Dining space and illuminated staircase',
     'A dining area and staircase united by concealed linear light, black pendants and recessed spots.',
     ['homepg-4']),
    ('Warm evening living room', 'Residential interior', 'homepg-6', 'Living room with warm cove, wall-panel and table lighting',
     'Warm perimeter cove light, illuminated wall panels and portable lamps shape a relaxed evening living room.',
     ['homepg-5']),
    ('Garden courtyard dining', 'Landscape & pathways', 'homepg-1', 'Illuminated courtyard seating area with tree and garden lights',
     'Garden lights, tree uplights and warm terrace light turn a paved courtyard into an evening dining setting.',
     ['homepg-3', 'pg-2']),
]
