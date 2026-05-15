class ProcessExtractionJob < ApplicationJob
  queue_as :default

  def perform(extraction_id, password: nil)
    extraction = Extraction.find(extraction_id)
    extraction.update!(status: :processing, error_message: nil)

    extraction.source_pdf.blob.open do |file|
      result = PythonExtractorRunner.new(input_path: file.path, password: password).call

      extraction.result_xlsx.purge if extraction.result_xlsx.attached?
      extraction.result_xlsx.attach(
        io: StringIO.new(result.xlsx_binary),
        filename: "#{File.basename(extraction.original_filename, ".*")}.xlsx",
        content_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      )

      extraction.update!(
        status: :completed,
        error_message: nil,
        columns: result.columns,
        rows: result.rows,
        transaction_count: result.transaction_count
      )
    end
  rescue PythonExtractorRunner::PasswordRequiredError => e
    extraction.update!(
      status: :password_required,
      error_message: e.message,
      columns: [],
      rows: [],
      transaction_count: 0
    )
  rescue PythonExtractorRunner::UnsupportedStatementError => e
    extraction.update!(
      status: :failed,
      error_message: e.message,
      columns: [],
      rows: [],
      transaction_count: 0
    )
  rescue StandardError => e
    extraction.update!(
      status: :failed,
      error_message: "Unexpected processing failure: #{e.message}",
      columns: [],
      rows: [],
      transaction_count: 0
    )
    Rails.logger.error("ProcessExtractionJob failed for #{extraction_id}: #{e.class} #{e.message}")
  end
end
