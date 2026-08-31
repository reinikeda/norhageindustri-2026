from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "gif")
DOCUMENT_EXTENSIONS = ("pdf", "doc", "docx", "xls", "xlsx")

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_DOCUMENT_BYTES = 15 * 1024 * 1024

validate_image_extension = FileExtensionValidator(IMAGE_EXTENSIONS)
validate_document_extension = FileExtensionValidator(DOCUMENT_EXTENSIONS)


def _validate_size(file, max_bytes, label):
    size = getattr(file, "size", None)
    if size is None:
        return
    if size > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        raise ValidationError(f"{label} must be {max_mb} MB or smaller.")


def validate_image_file(file):
    validate_image_extension(file)
    _validate_size(file, MAX_IMAGE_BYTES, "Images")


def validate_document_file(file):
    validate_document_extension(file)
    _validate_size(file, MAX_DOCUMENT_BYTES, "Documents")
