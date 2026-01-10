"""
Internationalization (i18n) support for email2print
Add new languages by creating a new dictionary following the same structure
"""

TRANSLATIONS = {
    "en": {
        # Log messages
        "starting_script": "Starting email2print script",
        "monitoring_inbox": "Monitoring inbox: {email}",
        "printing_to": "Printing to printer: {printer}",
        "scan_interval": "Scan interval: {seconds} seconds",
        "max_file_size": "Max file size: {mb} MB",
        "connecting_imap": "Connecting to IMAP server (attempt {attempt}/{max_attempts})",
        "imap_connected": "IMAP connection established successfully",
        "imap_failed": "IMAP connection attempt {attempt} failed: {error}",
        "max_retries_reached": "Max IMAP connection retries reached. Raising exception.",
        "retrying_in": "Retrying in {seconds} seconds...",
        "found_messages": "Found {count} unseen messages",
        "no_new_messages": "No new messages.",
        "processing_email": "Processing email from: {sender}",
        "email_subject": "Subject: {subject}",
        "valid_attachments_found": "Valid attachments found. Email body will be SKIPPED.",
        "attachment_empty": "Attachment '{filename}' ({content_type}) is empty. Skipping print.",
        "body_empty": "Email body ({content_type}) is empty. Skipping print.",
        "attachment_not_allowed": "Attachment '{filename}' type .{ext} not allowed. Skipping.",
        "html_blank": "HTML email body is blank after stripping tags. Skipping.",
        "printing_attachment": "Printing attachment '{filename}': {path}",
        "printing_body": "Printing email body ({content_type}): {path}",
        "sent_to_printer": "Sent to printer: {printer} - File: {path}",
        "printing_failed": "Printing failed for {path}: {error}",
        "libreoffice_conversion_required": "File type .{ext} requires LibreOffice conversion",
        "libreoffice_conversion_success": "LibreOffice conversion successful: {input} -> {output}",
        "libreoffice_conversion_failed": "LibreOffice conversion failed: PDF not found at {path}",
        "libreoffice_conversion_failed_cannot_print": "Failed to convert {path}, cannot print",
        "libreoffice_timeout": "LibreOffice conversion timeout for {path}",
        "libreoffice_error": "LibreOffice conversion failed for {path}: {error}",
        "libreoffice_unexpected_error": "Unexpected error during LibreOffice conversion: {error}",
        "temp_cleanup_failed": "Failed to clean up temp files: {error}",
        "deleted_temp_file": "Deleted temporary file: {path}",
        "failed_delete_temp": "Failed to delete temp file {path}: {error}",
        "no_printable_content": "No printable content found in this email.",
        "sending_confirmation": "Sending confirmation email to {email}",
        "confirmation_sent": "Confirmation email sent.",
        "confirmation_failed": "Error sending confirmation email: {error}",
        "email_marked_deletion": "Email {uid} marked for deletion.",
        "messages_expunged": "Deleted messages expunged from server.",
        "sleeping": "Sleeping {seconds}s...",
        "unexpected_error": "Unexpected error in main loop: {error}",
        "sender_not_allowed": "Sender {sender} not in ALLOWED_RECIPIENTS (nor domain match). Skipping print.",
        "allowed_recipients_empty": "ALLOWED_RECIPIENTS is empty. Denying sender: {sender}",
        "file_exceeds_size": "{description} exceeds max size ({mb}MB). Skipping.",
        "missing_env_var": "Missing required environment variable: {var}",
        
        # Confirmation email
        "confirmation_subject_default": "Your Print Job Confirmation",
        "confirmation_processed": "Your print job was processed:\n\n{log}",
        "confirmation_printed": "{timestamp} – Your file '{filename}' was printed on printer '{printer}'",
        "confirmation_no_files": "No files were printed.",
    },
    
    "es": {
        # Log messages
        "starting_script": "Iniciando script email2print",
        "monitoring_inbox": "Monitoreando bandeja: {email}",
        "printing_to": "Imprimiendo en impresora: {printer}",
        "scan_interval": "Intervalo de escaneo: {seconds} segundos",
        "max_file_size": "Tamaño máximo de archivo: {mb} MB",
        "connecting_imap": "Conectando al servidor IMAP (intento {attempt}/{max_attempts})",
        "imap_connected": "Conexión IMAP establecida exitosamente",
        "imap_failed": "Intento {attempt} de conexión IMAP falló: {error}",
        "max_retries_reached": "Máximo de reintentos IMAP alcanzado. Lanzando excepción.",
        "retrying_in": "Reintentando en {seconds} segundos...",
        "found_messages": "Se encontraron {count} mensajes no leídos",
        "no_new_messages": "No hay mensajes nuevos.",
        "processing_email": "Procesando correo electrónico de: {sender}",
        "email_subject": "Asunto: {subject}",
        "valid_attachments_found": "Se encontraron archivos adjuntos válidos. El cuerpo del correo electrónico será OMITIDO.",
        "attachment_empty": "Adjunto '{filename}' ({content_type}) está vacío. Omitiendo impresión.",
        "body_empty": "Cuerpo del correo electrónico ({content_type}) está vacío. Omitiendo impresión.",
        "attachment_not_allowed": "Adjunto '{filename}' tipo .{ext} no permitido. Omitiendo.",
        "html_blank": "Cuerpo HTML del correo electrónico está vacío después de quitar etiquetas. Omitiendo.",
        "printing_attachment": "Imprimiendo adjunto '{filename}': {path}",
        "printing_body": "Imprimiendo cuerpo del correo electrónico ({content_type}): {path}",
        "sent_to_printer": "Enviado a impresora: {printer} - Archivo: {path}",
        "printing_failed": "Impresión falló para {path}: {error}",
        "libreoffice_conversion_required": "Tipo de archivo .{ext} requiere conversión con LibreOffice",
        "libreoffice_conversion_success": "Conversión LibreOffice exitosa: {input} -> {output}",
        "libreoffice_conversion_failed": "Conversión LibreOffice falló: PDF no encontrado en {path}",
        "libreoffice_conversion_failed_cannot_print": "Falló la conversión de {path}, no se puede imprimir",
        "libreoffice_timeout": "Timeout en conversión LibreOffice para {path}",
        "libreoffice_error": "Conversión LibreOffice falló para {path}: {error}",
        "libreoffice_unexpected_error": "Error inesperado durante conversión LibreOffice: {error}",
        "temp_cleanup_failed": "Falló la limpieza de archivos temporales: {error}",
        "deleted_temp_file": "Archivo temporal eliminado: {path}",
        "failed_delete_temp": "Falló la eliminación del archivo temporal {path}: {error}",
        "no_printable_content": "No se encontró contenido imprimible en este correo electrónico.",
        "sending_confirmation": "Enviando correo electrónico de confirmación a {email}",
        "confirmation_sent": "Correo electrónico de confirmación enviado.",
        "confirmation_failed": "Error al enviar correo electrónico de confirmación: {error}",
        "email_marked_deletion": "Correo electrónico {uid} marcado para eliminación.",
        "messages_expunged": "Mensajes eliminados purgados del servidor.",
        "sleeping": "Esperando {seconds}s...",
        "unexpected_error": "Error inesperado en bucle principal: {error}",
        "sender_not_allowed": "Remitente {sender} no está en ALLOWED_RECIPIENTS (ni coincide dominio). Omitiendo impresión.",
        "allowed_recipients_empty": "ALLOWED_RECIPIENTS está vacío. Denegando remitente: {sender}",
        "file_exceeds_size": "{description} excede el tamaño máximo ({mb}MB). Omitiendo.",
        "missing_env_var": "Falta variable de entorno requerida: {var}",
        
        # Confirmation email
        "confirmation_subject_default": "Confirmación de tu Trabajo de Impresión",
        "confirmation_processed": "Tu trabajo de impresión fue procesado:\n\n{log}",
        "confirmation_printed": "{timestamp} – Tu archivo '{filename}' fue impreso en la impresora '{printer}'",
        "confirmation_no_files": "No se imprimieron archivos.",
    }
}

def get_translation(key, lang="en", **kwargs):
    """
    Get translated string for a given key and language.
    Falls back to English if language or key not found.
    
    Args:
        key: Translation key
        lang: Language code (e.g., 'en', 'es')
        **kwargs: Format parameters for the translation string
    
    Returns:
        Translated and formatted string
    """
    # Get translation with fallback to English
    translation = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS["en"].get(key, key)
    
    # Format with provided parameters if any
    try:
        return translation.format(**kwargs)
    except KeyError:
        # If format fails, return the raw translation
        return translation

def get_available_languages():
    """Return list of available language codes"""
    return list(TRANSLATIONS.keys())
