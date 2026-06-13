from itertools import batched

from PIL import Image


def rgb_batches(data: list[int], include_length: bool = False) -> tuple[tuple[int]]:
    """transoforms bytes to rgb batches (tuple of 3 ints)"""

    if include_length:
        length_bytes = len(data).to_bytes(3, "big")
        data = list(length_bytes) + data

    while len(data) % 3 != 0:
        data.append(0)

    return tuple(batched(data, 3, strict=True))


def encode_text_to_image(text: str, filename: str) -> None:
    data = list(text.encode("utf-8"))
    img_data = rgb_batches(data, True)

    img = Image.new("RGB", (32, 32))
    img.putdata(img_data)
    img.save(filename)


def load_image_data(filename: str) -> list[tuple[int, int, int]]:
    img = Image.open(filename)
    return list(img.get_flattened_data())


def extract_size(img_data: list[tuple[int, int, int]]) -> int:
    size_tuple = img_data.pop(0)
    return int.from_bytes(size_tuple, "big")


def extract_bytes(img_data: list[tuple[int, int, int]], size: int) -> bytes:
    data = []

    for pixel in img_data:
        data.extend(pixel)

    data = data[:size]
    return bytes(data)


def decode_text_from_image(filename: str) -> str:
    img_data = load_image_data(filename)

    size = extract_size(img_data)
    data = extract_bytes(img_data, size)

    return data.decode("utf-8")


def main():
    text = input("Enter text:")

    filename = "test.png"
    encode_text_to_image(text, filename)
    print("Encoded text to image test.png")

    decoded_text = decode_text_from_image("test.png")
    print(f"Decoded text from image {filename}: {decoded_text}")


main()
