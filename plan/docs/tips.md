## Tips & Lessons Learned

- **Gradio image previews need file-backed data.** When we returned in-memory `PIL.Image` objects directly from `handle_generate_image()`, Gradio's component routinely stayed blank until the same image was later reloaded from disk. After several attempts (role normalization, base64 payloads, NumPy arrays) we concluded that relying on Gradio's filepath mode is the only stable approach in this app. The current workflow simply saves the draft image when the user clicks "Show Image," which simultaneously reveals the preview and keeps the bytes available for persistence.

