"""Starter copy for editable listing pages. Used to seed PageContent and as a fallback."""

PAGE_DEFAULTS = {
    'products': dict(eyebrow='The NCCT collection', heading='Lighting products',
        intro='Explore the collection. Find the light for your setting.',
        seo_title='Lighting products', seo_description='Discover NCCT lighting by category, model and technical characteristics. Browse product details and download available datasheets.'),
    'projects': dict(eyebrow='Light & architecture', heading='Projects *in light.*',
        intro='A showcase of the interior, outdoor and landscape settings NCCT lighting is designed for. Each story shows how light shapes a space.',
        notice='“Lighting reference” stories use imagery from the NCCT image library to illustrate the settings our lighting suits. They do not name clients or claim delivery of a specific commission. Delivered projects are marked as such once confirmed.',
        cta_eyebrow='Your next project', cta_heading='Let’s bring your space to light.', cta_text='Start a project enquiry',
        seo_title='Projects', seo_description='Explore NCCT lighting project showcases across interior, outdoor and landscape lighting, and discuss your project requirements with our team.'),
    'resources': dict(eyebrow='For architects & specifiers', heading='Resources & downloads',
        intro='Technical information, ready for your next project.',
        seo_title='Resources & downloads', seo_description='Download available lighting datasheets and technical documents supplied on the NCCT website.'),
    'solutions': dict(eyebrow='A considered approach', heading='Lighting solutions',
        intro='The right light for your setting.',
        seo_title='Lighting solutions', seo_description='Explore indoor, outdoor, decorative, industrial and professional lighting with NCCT.'),
    'contact': dict(eyebrow='Start a conversation', heading='Contact NCCT',
        intro='Tell us about your space, a product or a project. The team will review your enquiry and get in touch.',
        seo_title='Contact NCCT', seo_description='Contact the NCCT team in Business Bay, Dubai. Discuss lighting products, technical information or your project requirements.'),
    'about': dict(cta_eyebrow='Start a conversation', cta_heading='Tell us about your space.', cta_text='Send an enquiry'),
}
