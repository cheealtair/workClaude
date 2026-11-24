import sys
import pypdfium2 as pdfium

pdf_path, out_dir = sys.argv[1], sys.argv[2]
pdf = pdfium.PdfDocument(pdf_path)
print("pages", len(pdf))
for i in range(len(pdf)):
    page = pdf[i]
    w, h = page.get_size()
    scale = 1920.0 / w
    img = page.render(scale=scale).to_pil().convert("RGB")
    if img.size != (1920, 1080):
        print("size", i + 1, img.size, "from", w, h)
        img = img.resize((1920, 1080))
    img.save("%s/slide-%02d.png" % (out_dir, i + 1))
print("done")
