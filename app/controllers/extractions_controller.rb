class ExtractionsController < ApplicationController
  before_action :set_extraction, only: %i[show update_password download]

  def new
    @extraction = Extraction.new
  end

  def create
    @extraction = Extraction.new(status: :queued, user: current_user)
    @extraction.guest_token = guest_token unless signed_in?
    source_pdf = extraction_params[:source_pdf]

    validate_source_pdf(source_pdf)

    if source_pdf.present?
      @extraction.original_filename = source_pdf.original_filename.to_s
      @extraction.source_pdf.attach(source_pdf)
    end

    if @extraction.errors.empty? && @extraction.save
      ProcessExtractionJob.perform_later(@extraction.id, password: extraction_params[:password].presence)
      redirect_to extraction_path(@extraction), notice: "Your statement is queued for extraction."
    else
      render :new, status: :unprocessable_entity
    end
  end

  def show
  end

  def update_password
    if extraction_params[:password].blank?
      redirect_to extraction_path(@extraction), alert: "Enter the PDF password to retry."
      return
    end

    unless @extraction.password_required?
      redirect_to extraction_path(@extraction), alert: "This extraction does not need a password retry."
      return
    end

    @extraction.update!(status: :queued, error_message: nil)
    ProcessExtractionJob.perform_later(@extraction.id, password: extraction_params[:password])

    redirect_to extraction_path(@extraction), notice: "Password received. The extraction has been queued again."
  end

  def download
    unless @extraction.completed? && @extraction.result_xlsx.attached?
      redirect_to extraction_path(@extraction), alert: "The Excel export is not ready yet."
      return
    end

    redirect_to rails_blob_path(@extraction.result_xlsx, disposition: "attachment")
  end

  private

  def set_extraction
    @extraction =
      if signed_in?
        Extraction.where(user: current_user).or(Extraction.where(guest_token: guest_token)).find(params[:id])
      else
        Extraction.where(guest_token: guest_token).find(params[:id])
      end
  end

  def extraction_params
    params.fetch(:extraction, {}).permit(:source_pdf, :password)
  end

  def validate_source_pdf(source_pdf)
    if source_pdf.blank?
      @extraction.errors.add(:source_pdf, "must be attached")
      return
    end

    return if source_pdf.content_type.to_s == "application/pdf"

    @extraction.errors.add(:source_pdf, "must be a PDF file")
  end
end
