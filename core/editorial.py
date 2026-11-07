"""Editorial guidance, separate from product specifications and administrator records.

General education is versioned with the site; no database write is required to deploy it.
"""
from django.urls import reverse

SOLUTION_COPY = {
'indoor': ('Comfort, character and clarity for interior spaces.', 'Ceiling, wall and recessed lighting can provide general illumination, while directional and task lighting support specific activities.', 'Homes, offices, retail interiors, restaurants and circulation spaces.', ['Plan ambient, task and accent light separately.', 'Review ceiling depth, mounting and maintenance access.', 'Compare colour rendering, glare and the light distribution at the working plane.'], 'Ceiling luminaires, wall fittings, recessed fittings and directional spotlights.'),
'outdoor': ('Illumination that supports exterior architecture and movement.', 'Exterior lighting helps reveal entrances, paths and architectural surfaces after dark. Select fittings for the actual exposure and mounting conditions.', 'Facades, landscaped gardens, paths, entrances and public circulation areas.', ['Consider rain, dust, drainage and local environmental exposure.', 'Aim light at the intended surface and limit spill beyond it.', 'Check mounting, corrosion resistance and access for maintenance.'], 'Bollards, inground fittings, wall luminaires and adjustable spotlights.'),
'decorative': ('Lighting that becomes part of the design.', 'A decorative fitting contributes form and material to a room as well as illumination. Its appearance should work with the surrounding light, rather than replace every other lighting layer.', 'Hospitality interiors, homes, restaurants, cafes and reception spaces.', ['Check scale, suspension height and sightlines.', 'Coordinate finish and colour appearance with the interior.', 'Confirm lamp or driver compatibility and dimming needs.'], 'Pendant, wall, table and other decorative lighting families.'),
'industrial': ('Practical solutions for demanding environments.', 'Industrial lighting is selected around the work being carried out, the physical space and its operating conditions. Mounting height and the distribution of light influence usable illumination.', 'Warehouses, workshops, industrial spaces and service areas.', ['Assess the task, obstructions and mounting height.', 'Check temperature, dust and moisture suitability.', 'Review maintenance access, electrical compatibility and light distribution.'], 'Industrial pendants and functional luminaires, subject to the listed product specification.'),
'professional': ('Focused lighting for specialised applications.', 'Professional lighting responds to the particular needs of displays, studios and presentations. Direction, control and the appearance of illuminated subjects can matter as much as total output.', 'Exhibitions, displays, studios and presentation environments.', ['Consider aiming range, beam distribution and spill.', 'Review colour rendering and control requirements.', 'For camera use, request product-specific flicker and dimming information.'], 'Directional and specialist lighting equipment in the professional collection.'),
'led': ('Versatile illumination for contemporary architectural settings.', 'LED lighting is a source technology used in many kinds of luminaires. Choose the complete fitting or system by its delivered light, installation requirements and compatibility.', 'Interior details, commercial buildings, architectural lines and display features.', ['Compare lumens and electrical input for the complete product.', 'Check the thermal environment and installation instructions.', 'Confirm driver type, control interface and colour consistency.'], 'LED luminaires, modules and linear products where listed in the catalogue.'),
'control': ('Compatible components for considered lighting systems.', 'Control gear supplies or manages the electrical operation of a lighting product. Components must be selected as a compatible system, not simply by matching a wattage number.', 'Interior lighting, dimming systems and controlled commercial installations.', ['Confirm constant-current or constant-voltage operation.', 'Match output range, load and the control protocol.', 'Allow appropriate ventilation and maintenance access.'], 'Drivers and control components with verified electrical compatibility.'),
'lamps': ('Light sources selected for the fitting and the task.', 'Replacement lamps need to match both the physical fitting and its electrical requirements. Colour appearance, output and distribution then determine how the replacement will perform in the space.', 'Compatible residential, commercial and decorative fittings.', ['Check cap, dimensions, supply and enclosure suitability.', 'Compare lumens rather than wattage alone.', 'Confirm dimmer compatibility where dimming is required.'], 'The lamp types and formats shown in the current collection.'),
'emergency': ('Lighting for the specified emergency function.', 'Emergency lighting has a distinct role when normal lighting is interrupted. Product selection must follow the project design and applicable requirements, with verified operating information for the exact model.', 'Escape routes, circulation areas and other spaces identified by the project design.', ['Confirm the required operating mode and rated duration.', 'Check installation, testing and maintenance requirements.', 'Request the relevant model documentation before specifying.'], 'Emergency lighting products identified in the catalogue; suitability requires project-specific confirmation.'),
}

def solution_copy(name):
    key = next((key for key in SOLUTION_COPY if key in name.lower()), None)
    if not key:
        return None
    intro, explanation, uses, considerations, types = SOLUTION_COPY[key]
    return dict(intro=intro, explanation=explanation, uses=uses, considerations=considerations, types=types)

# Each guide contains a distinct explanation, a practical comparison and a next step.
GUIDE_ROWS = [
('colour-temperature','Understanding Colour Temperature','Technical guides','How warm, neutral and cool light affect a space.',
 'Colour temperature describes the colour appearance of white light and is expressed in kelvin (K). Lower values generally appear warmer; higher values appear cooler. It does not tell you how much light a fitting produces or how accurately it renders materials.',
 'Compare samples against the actual finishes. Timber, stone, paint and textiles can look different under different sources. Keep the intended atmosphere and the relationship between neighbouring areas in mind, rather than selecting a value in isolation.',
 'Record the required colour temperature when enquiring. For mixed fittings, ask about consistency across the specified models and confirm whether any colour adjustment is available.'),
('colour-rendering','Understanding Colour Rendering','Technical guides','How a light source influences the appearance of materials.',
 'Colour rendering concerns how objects appear under a light source compared with a reference source. CRI is a commonly quoted measure, but a single average cannot describe every colour or every visual preference.',
 'Two sources with the same colour temperature can still show materials differently. Where appearance is important, review samples of finishes, merchandise or artwork under the proposed light. Request more detailed colour information if the application requires it.',
 'Use the exact model datasheet and ask which colour-rendering data applies to the configuration being considered. Do not infer colour performance from a product photograph.'),
('lumens-lux-distribution','Lumens, Lux and Lighting Distribution','Technical guides','Distinguish total output from the light reaching a surface.',
 'Lumens describe luminous flux: the amount of visible light emitted. Lux describes illuminance: light arriving per unit area, with one lux equal to one lumen per square metre. They answer different questions.',
 'A high lumen figure does not guarantee the desired illuminance at a desk or pathway. Mounting height, optical distribution, spacing, surface reflectance and obstructions affect the result. A focused beam and a broad beam can deliver the same total output very differently.',
 'For a project comparison, provide dimensions, mounting positions and the task being illuminated. Request photometric information for the selected product when a lighting calculation is needed.'),
('beam-angle','Understanding Beam Angle','Technical guides','Choose between focused light and wider coverage.',
 'Beam angle is a way of describing the spread of a directional source. A narrower beam concentrates light into a smaller area; a wider beam distributes it more broadly. The edge of a beam is not necessarily a sharp boundary.',
 'The illuminated footprint grows as the distance from the fitting increases. Review the actual distribution and aiming angle, especially when highlighting a wall, object or landscape feature. Beam angle alone does not describe every part of an asymmetric distribution.',
 'Share the target size, mounting distance and desired effect. Confirm the available optic for the exact product and ask for its distribution information where needed.'),
('ip-ratings','Understanding IP Ratings','Technical guides','Assess protection against solids and water.',
 'An IP code describes enclosure protection against access or solid objects and water under defined tests. The first digit concerns solids; the second concerns water. The two digits describe separate aspects of protection.',
 'The rating is not a general guarantee of outdoor suitability. Corrosion, UV exposure, temperature, drainage, impact and installation can also matter. A rating for one water exposure should not be assumed to cover every other exposure.',
 'Describe the installation conditions and use the manufacturer documentation for the exact model. Confirm any installation limitations and maintenance requirements before specifying.'),
('efficiency-wattage','Lighting Efficiency and Wattage','Technical guides','Compare useful light output with electrical input.',
 'Watts describe electrical power, not brightness. Luminous efficacy relates output in lumens to input power in watts. Compare equivalent measurement boundaries: an LED component figure is not necessarily the performance of a complete luminaire.',
 'Optics, drivers and operating conditions affect the final result. A fitting with an efficient source may still distribute light poorly for a particular task. Consider useful illumination, comfort and operating needs alongside the stated efficacy.',
 'Use complete-product data for the selected configuration. Ask for output, input power and the conditions under which those values were measured.'),
('controls-dimming','Lighting Controls and Dimming','Technical guides','Treat the light source, driver and controller as a system.',
 'Controls can change how and when lighting operates. Switching, dimming and scene control are different functions. A product being LED-based does not automatically mean that it supports the required dimming method.',
 'Compatibility depends on the driver, controller, connected load and wiring arrangement. Confirm the supported interface and operating range. Low-level behaviour, flicker and minimum load can differ between combinations.',
 'Share the control system or dimmer model before ordering. Request confirmation for the complete combination and a sample test where performance is critical.'),
('glare','Understanding Glare','Technical guides','Balance brightness with visual comfort.',
 'Glare can occur when bright sources or reflections interfere with comfortable viewing. The same luminaire can feel different depending on where it is mounted, what surrounds it and the direction from which it is seen.',
 'Consider shielding, source visibility, aiming and the brightness of nearby surfaces. Reflective desks, screens and polished materials can introduce distracting reflections. Simply reducing output may not address an unsuitable position or optic.',
 'Review viewing directions and the tasks taking place. Request relevant photometric information and evaluate the proposed arrangement, rather than judging comfort by a product image.'),
('layered-lighting','Layered Lighting','Application knowledge','Combine ambient, task and accent lighting deliberately.',
 'Ambient lighting supports overall orientation. Task lighting helps a specific activity. Accent lighting gives emphasis to selected objects or surfaces. These functions can overlap, but separating them during planning makes the purpose of each fitting clearer.',
 'Begin with the activities and the desired visual hierarchy. Add task light where it is useful and accent light where emphasis is intentional. Separate control groups can help a space respond to different times and activities.',
 'Sketch the areas and activities before selecting fittings. Share the mounting constraints and identify which lighting groups should operate together.'),
('selecting-indoor-lighting','Selecting Indoor Lighting','Lighting selection','Start with activities, surfaces and installation constraints.',
 'An indoor selection starts with what happens in the room. Reading, circulation, display and conversation create different lighting needs. Consider the relationship between daylight and electric light as well as the appearance of the fittings.',
 'Check ceiling construction, available recess depth, mounting locations and the route for wiring. Compare light distribution, colour appearance and visual comfort. Use task or accent lighting where a uniform general layout would be insufficient.',
 'Prepare room dimensions, finishes, mounting options and control requirements. Shortlist products with the right installation format before comparing their documented performance.'),
('selecting-outdoor-lighting','Selecting Outdoor Lighting','Lighting selection','Match the fitting to exposure, direction and context.',
 'Outdoor lighting should have a clear purpose: reveal an entrance, support a path, emphasise a surface or illuminate a working area. Start by identifying the target rather than lighting every surface equally.',
 'Assess exposure to rain, dust, standing water and corrosive conditions. Review mounting, drainage and maintenance access. Control the direction and operating hours to reduce unnecessary light spill and avoid distracting neighbouring spaces.',
 'Provide the installation position and exposure conditions. Confirm the exact product rating, material suitability, optic and installation instructions with the supplier.'),
('driver-compatibility','Product and Driver Compatibility','Lighting selection','Check the electrical relationship before selecting components.',
 'A driver must match the electrical requirements of the light source. Constant-current and constant-voltage systems are different. A matching power figure alone does not establish compatibility.',
 'Check output voltage or current, the permitted load range, supply requirements and any control interface. Cable lengths, ambient conditions and enclosure space can influence installation requirements. Follow the product documentation for permitted combinations.',
 'Provide the exact luminaire and driver references when asking for a replacement or new combination. Electrical selection and installation should be confirmed by a competent professional.'),
('architectural-lighting','Why Architectural Lighting Matters','Insights','Use light to make architecture legible.',
 'Lighting influences which parts of a building are noticed and how its proportions are understood. A softly illuminated plane can establish the room, while a focused detail creates a point of attention.',
 'Start with the architecture: the material, texture, geometry and intended use. Decide which elements should be quiet and which deserve emphasis. A considered hierarchy often communicates more clearly than illuminating every surface at the same brightness.',
 'Use drawings and material samples to explain the intended effect. Compare fitting positions and distribution before selecting the final product form.'),
('importance-of-lighting-layers','The Importance of Lighting Layers','Insights','Give a space more than one lighting condition.',
 'A single lighting layer often asks one fitting to perform several unrelated jobs. Separate layers allow general visibility, close work and visual emphasis to be considered on their own terms.',
 'In a restaurant, table lighting, circulation light and the treatment of walls can have different roles. In an office, desk tasks and meeting spaces may need different arrangements. The useful distinction is functional, not a requirement to add more fixtures.',
 'List the activities and the scenes the space needs. Group compatible fittings so the controls support those activities without making everyday operation complicated.'),
('light-and-shadow','Designing With Light and Shadow','Insights','Use contrast to reveal form without losing visibility.',
 'Shadow helps make depth and texture visible. Lighting from different directions can flatten a surface or reveal its relief. The appropriate balance depends on what the viewer needs to see.',
 'Avoid treating darkness as a defect everywhere. Retain quieter areas where appropriate, while ensuring circulation and tasks remain clearly legible. Check the effect from normal viewing positions rather than only from the intended photograph angle.',
 'Review a sample or mock-up for textured materials. Adjust direction and intensity together, and check that the result remains comfortable for occupants.'),
('outdoor-identity','Outdoor Lighting and Architectural Identity','Insights','Make a building readable after dark.',
 'A nighttime lighting scheme can reveal the structure, rhythm and entrances of a building without reproducing its daytime appearance. The aim is a clear relationship between illuminated features and the wider setting.',
 'Choose the surfaces that matter most. Coordinate facade treatment with paths and entrances so the visual hierarchy remains coherent. Consider nearby residents, landscape features and the operating schedule.',
 'Document target surfaces, viewpoints and mounting constraints. Confirm optics and environmental suitability before interpreting a reference image as a product specification.'),
('commercial-interiors','Choosing Lighting for Commercial Interiors','Insights','Balance practical tasks with presentation.',
 'Commercial interiors combine work, movement and communication. The useful lighting arrangement depends on the activity: merchandise presentation, screen-based work, reception and circulation each have different visual priorities.',
 'For offices, review tasks and reflections. For retail, consider how merchandise colours and surfaces appear. For cafes and hospitality, balance atmosphere with readable menus, visible routes and comfortable faces.',
 'Create a brief covering tasks, finishes, mounting and operating hours. Use actual product data and appropriate project design criteria to compare the shortlisted options.'),
('decorative-functional','Decorative and Functional Lighting','Insights','Let appearance and useful illumination work together.',
 'A decorative luminaire contributes to the visual character of a room even when it is off. Its shape and material are part of the interior, but they do not alone establish how well the room will be lit.',
 'Check the direction of light, source visibility and output alongside dimensions and finish. A statement pendant may benefit from separate task or wall lighting. Equally, a quiet architectural fitting can support the setting without competing with it.',
 'Consider the decorative fitting within a complete lighting plan. Confirm its lamp or driver requirements and identify the other layers needed for the activities below it.'),
('technical-specifications','Why Technical Specifications Matter','Insights','Compare the exact configuration, not a product family name.',
 'A product photograph shows appearance. A specification describes the characteristics needed to decide whether a particular configuration suits a project. Different versions of the same family can have different optics, output and electrical requirements.',
 'Compare model reference, dimensions, mounting, supply, output, distribution, colour characteristics, protection and controls. Mark missing information as a question rather than filling it with assumptions. Check the date and configuration of the supporting document.',
 'Send the exact product reference and application to NCCT. Ask for the relevant datasheet and confirmation of any unresolved installation or compatibility requirements.'),
]
GUIDES = [dict(slug=s, title=t, group=g, intro=i, sections=[('What it means',a),('What to consider',b),('Before you enquire',c)]) for s,t,g,i,a,b,c in GUIDE_ROWS]
GUIDE_BY_SLUG = {g['slug']: g for g in GUIDES}

APPLICATIONS = [
 ('Residential spaces','Balance ambient, task and accent light for everyday comfort. Consider reading, cooking, circulation and rest separately.','indoor'),
 ('Offices & commercial buildings','Support work and wayfinding while considering screens, finishes and the appearance of shared areas.','indoor'),
 ('Hospitality, restaurants & cafes','Balance guest comfort, table lighting, readable routes and the atmosphere of the interior.','decorative'),
 ('Retail, exhibitions & displays','Direct attention to selected products and surfaces; review colour appearance and viewing positions.','professional'),
 ('Facades, gardens & landscapes','Coordinate architectural features, entrances and paths while controlling spill and exposure.','outdoor'),
 ('Public & circulation spaces','Help people read routes, entrances and changes in level with appropriate distribution and visual comfort.','outdoor'),
 ('Industrial & warehouse spaces','Begin with tasks, mounting heights, obstructions and the operating environment.','industrial'),
]
FAQS = [
 ('Which lighting categories can I explore?','Browse indoor, outdoor, decorative, industrial, professional and LED lighting, together with control gear, lamps and emergency lighting. The catalogue shows the currently published products.'),
 ('How do I choose a product?','Start with the application, installation position and visual task. Compare the model description, available technical data and compatible controls. Send the relevant details to NCCT when suitability is uncertain.'),
 ('Where can I find specifications and datasheets?','Product pages show verified information where available. Linked downloads also appear in Resources. If a document or a value is missing, request it using the product reference; a blank field is not a performance claim.'),
 ('Does colour temperature tell me how bright a light is?','No. It describes the colour appearance of white light. Compare luminous output and distribution separately, and consider the light reaching the intended surface.'),
 ('How should I choose a beam angle?','Consider the target area, mounting distance and aiming direction. A narrow distribution concentrates light; a wider distribution covers more area. Ask for the available optic for the exact model.'),
 ('Does an IP rating guarantee outdoor suitability?','No. It describes particular enclosure protection tests. Also review exposure, materials, drainage, temperature and the installation instructions for the application.'),
 ('Can any LED driver be used with a fitting?','No. Match the required current or voltage, load range and control interface. Confirm the exact combination with the product documentation and a competent installer.'),
 ('Can indoor products be installed outside?','Do not assume so. Use a product documented as suitable for the actual environmental and installation conditions.'),
 ('Are all LED products dimmable?','No. Dimming depends on the complete light source, driver and controller combination. State your control system when enquiring.'),
 ('What should a product enquiry include?','Include the model or product name, quantity if known, application, mounting conditions and required technical information. Drawings and installation details can be discussed with the team.'),
 ('How do I contact NCCT?','Use the enquiry form, email info@ncctdxb.com or call +971 58 1310300. The office is in Ubora Tower, Business Bay, Dubai.'),
]

def application_links(solutions):
    result=[]
    from .application_content import APPLICATION_PAGES
    for (title, text, key), detail in zip(APPLICATIONS, APPLICATION_PAGES):
        match=next((s for s in solutions if key in s.name.lower()), None)
        if match:
            result.append(dict(title=title, text=text, url=reverse('application-detail', args=[detail['slug']]), solution_url=match.get_absolute_url()))
    return result
