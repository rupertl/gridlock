**Objective:** Extract the source code embedded within the attached PNG image file as plain text, preserving the exact row and column structure. The image is expected to *only* contain source code.

**Input:** One PNG image file, containing only source code.

**Task:** Perform the following steps:

1.  **Optical Character Recognition (OCR) with Layout Preservation:** Apply Optical Character Recognition (OCR) to the entire image, ensuring that the output text accurately reflects the original row and column positioning of the characters in the image. This means maintaining line breaks, indentation and spacing. Operate on a line-by-line basis rather than scanning for regions of text.

2.  **Plain Text Output (Preserving Layout):** Output the recognized text as plain text, exactly as it appears visually in the image, including all whitespace.

**Specific Instructions and Considerations:**

* **Absolute Layout Accuracy:** The preservation of the original row and column structure is paramount. Ensure that the outputted text maintains the horizontal and vertical alignment visible in the image.
* **Full Image OCR:** Since the entire image is expected to be source code, apply OCR to the entire image area.
* **Handle Potential Noise:** Be prepared to handle potential noise or distortions in the image that might affect OCR accuracy in terms of character recognition and layout.
* **Expected Code Format:** Each line of code has 80 characters or fewer, including whitespace. All lines start with at least 5 spaces.
* **Single Code Block:** Assume each PNG file contains a single block of source code.
* **No Code Execution:** Do not attempt to execute the extracted code. The goal is purely text extraction with layout preservation.
* **Output Format:** The final output should be plain text that mirrors the visual layout of the code in the image. Do not output Python code to solve this problem. Do not output the steps you will take.
