import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [
    "input",
    "name",
    "dropzone",
    "error",
    "prompt",
    "button",
    "selected",
    "analysis",
    "analysisText",
    "passwordField"
  ]

  connect() {
    this.analysisToken = 0
  }

  choose() {
    const file = this.inputTarget.files[0]
    this.acceptFile(file)
  }

  dragEnter(event) {
    event.preventDefault()
    this.dropzoneTarget.classList.add("upload-dropzone--active")
  }

  dragOver(event) {
    event.preventDefault()
    event.dataTransfer.dropEffect = "copy"
    this.dropzoneTarget.classList.add("upload-dropzone--active")
  }

  dragLeave(event) {
    event.preventDefault()

    if (!this.dropzoneTarget.contains(event.relatedTarget)) {
      this.dropzoneTarget.classList.remove("upload-dropzone--active")
    }
  }

  drop(event) {
    event.preventDefault()
    this.dropzoneTarget.classList.remove("upload-dropzone--active")

    const file = event.dataTransfer.files[0]
    if (!file) return

    if (!this.isPdf(file)) {
      this.inputTarget.value = ""
      this.setFileName(null)
      this.showError("Only PDF files are accepted.")
      return
    }

    const transfer = new DataTransfer()
    transfer.items.add(file)
    this.inputTarget.files = transfer.files
    this.showError("")
    this.acceptFile(file)
  }

  clear() {
    this.analysisToken += 1
    this.inputTarget.value = ""
    this.setFileName(null)
    this.setPasswordVisible(false)
    this.setAnalyzing(false)
    this.showError("")
  }

  async acceptFile(file) {
    this.setFileName(file)
    this.setPasswordVisible(false)

    if (!file) return

    if (!this.isPdf(file)) {
      this.inputTarget.value = ""
      this.setFileName(null)
      this.showError("Only PDF files are accepted.")
      return
    }

    this.showError("")
    this.setAnalyzing(true)

    const token = ++this.analysisToken
    const encrypted = await this.detectEncryptedPdf(file)
    await this.fakeDelay(650)
    if (token !== this.analysisToken) return

    this.setAnalyzing(false)
    this.setPasswordVisible(encrypted)
  }

  isPdf(file) {
    return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
  }

  setFileName(file) {
    this.nameTarget.textContent = file ? file.name : ""
    this.selectedTarget.hidden = !file
    this.promptTarget.hidden = Boolean(file)
    this.buttonTarget.hidden = Boolean(file)

    this.dropzoneTarget.classList.toggle("upload-dropzone--has-file", Boolean(file))

    if (file && this.isPdf(file)) this.showError("")
  }

  setAnalyzing(active) {
    this.analysisTarget.hidden = !active
    this.dropzoneTarget.classList.toggle("upload-dropzone--analyzing", active)
    this.analysisTextTarget.textContent = active ? "Analyzing PDF protection..." : ""
  }

  setPasswordVisible(visible) {
    this.passwordFieldTarget.hidden = !visible

    const input = this.passwordFieldTarget.querySelector("input")
    if (!visible && input) input.value = ""
  }

  async detectEncryptedPdf(file) {
    const chunkSize = 1024 * 1024
    const firstChunk = await file.slice(0, chunkSize).text()
    const lastChunk = await file.slice(Math.max(file.size - chunkSize, 0), file.size).text()

    return `${firstChunk}\n${lastChunk}`.includes("/Encrypt")
  }

  fakeDelay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds))
  }

  showError(message) {
    if (this.hasErrorTarget) {
      this.errorTarget.textContent = message
    }
  }
}
