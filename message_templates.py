"""
WhatsApp Message Templates

This module contains all message templates used by the WhatsApp bot.
To add a new template, simply add a new function that returns a formatted string.

Template functions should:
- Accept **kwargs to allow flexible parameter passing
- Use .format() or f-strings for variable substitution
- Return a string with the complete message

Usage:
    from message_templates import get_message_template
    
    message = get_message_template("default", nombre="Juan")
    message = get_message_template("custom_template", nombre="María", empresa="Tech Corp")
"""


def default_template(**kwargs):
    """
    Default template for event sponsorship invitation
    
    Parameters:
        nombre (str): Contact name
    
    Returns:
        str: Formatted message
    """
    nombre = kwargs.get('nombre', 'Estimado/a')
    
    return f"""Hola {nombre},

El 18 de octubre realizaremos xxxx y queremos invitar a {nombre} como auspiciador.

La colaboración consiste en donar de forma voluntaria un producto, servicio o descuento. A cambio, recibirán:
- Promoción en nuestras redes sociales con un alcance orgánico de +2500 estudiantes.
Menciones en historias de Meta antes, durante y después del evento.
Publicaciones mostrando a los ganadores disfrutando de su producto o servicio.

¿Les interesaría unirse como auspiciadores?
Quedamos atentos a sus comentarios."""


def promotional_template(**kwargs):
    """
    Generic promotional template
    
    Parameters:
        nombre (str): Contact name
        producto (str): Product/service name
        descuento (str): Discount percentage or offer
    
    Returns:
        str: Formatted message
    """
    nombre = kwargs.get('nombre', 'Estimado/a')
    producto = kwargs.get('producto', 'nuestro producto')
    descuento = kwargs.get('descuento', 'una oferta especial')
    
    return f"""Hola {nombre},

Tenemos {descuento} en {producto} especialmente para ti.

¿Te gustaría conocer más detalles?

Quedamos atentos a tu respuesta."""


def event_invitation_template(**kwargs):
    """
    Event invitation template
    
    Parameters:
        nombre (str): Contact name
        evento (str): Event name
        fecha (str): Event date
        lugar (str): Event location
    
    Returns:
        str: Formatted message
    """
    nombre = kwargs.get('nombre', 'Estimado/a')
    evento = kwargs.get('evento', 'nuestro evento')
    fecha = kwargs.get('fecha', 'próximamente')
    lugar = kwargs.get('lugar', 'por definir')
    
    return f"""Hola {nombre},

Te invitamos a {evento}.

Fecha: {fecha}
Lugar: {lugar}

Esperamos contar con tu presencia.

Confirma tu asistencia respondiendo a este mensaje."""


def followup_template(**kwargs):
    """
    Follow-up template for previous conversations
    
    Parameters:
        nombre (str): Contact name
    
    Returns:
        str: Formatted message
    """
    nombre = kwargs.get('nombre', 'Estimado/a')
    
    return f"""Hola {nombre},

Siguiendo nuestra conversación anterior, me gustaría saber si tuviste oportunidad de revisar la información que compartimos.

¿Hay algo en lo que pueda ayudarte?

Quedo atento a tus comentarios."""


def thankyou_template(**kwargs):
    """
    Thank you template
    
    Parameters:
        nombre (str): Contact name
        motivo (str): Reason for thanking
    
    Returns:
        str: Formatted message
    """
    nombre = kwargs.get('nombre', 'Estimado/a')
    motivo = kwargs.get('motivo', 'tu apoyo')
    
    return f"""Hola {nombre},

Quiero agradecerte por {motivo}.

Tu colaboración es muy importante para nosotros.

¡Muchas gracias!"""


AVAILABLE_TEMPLATES = {
    "default": default_template,
    "promotional": promotional_template,
    "event_invitation": event_invitation_template,
    "followup": followup_template,
    "thankyou": thankyou_template,
}


def get_message_template(template_name="default", **kwargs):
    """
    Get a formatted message from a template
    
    Parameters:
        template_name (str): Name of the template to use
        **kwargs: Variables to pass to the template function
    
    Returns:
        str: Formatted message
    
    Raises:
        ValueError: If template_name doesn't exist
    
    Example:
        >>> msg = get_message_template("default", nombre="Juan")
        >>> msg = get_message_template("promotional", nombre="María", producto="Libro", descuento="20%")
    """
    if template_name not in AVAILABLE_TEMPLATES:
        raise ValueError(
            f"Template '{template_name}' not found. "
            f"Available templates: {', '.join(AVAILABLE_TEMPLATES.keys())}"
        )
    
    template_func = AVAILABLE_TEMPLATES[template_name]
    return template_func(**kwargs)


def list_templates():
    """
    List all available templates
    
    Returns:
        list: List of template names
    """
    return list(AVAILABLE_TEMPLATES.keys())


if __name__ == "__main__":
    print("Available Templates:")
    print("-" * 50)
    for template_name in list_templates():
        print(f"\n{template_name}:")
        print(get_message_template(template_name, nombre="Ejemplo"))
        print("-" * 50)