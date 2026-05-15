require "test_helper"

class ProcessExtractionJobTest < ActiveJob::TestCase
  test "completes extraction and attaches xlsx output" do
    extraction = build_extraction
    result = PythonExtractorRunner::Result.new(
      columns: ["Date", "Description"],
      rows: [["01JAN25", "Salary"]],
      transaction_count: 1,
      source_filename: "sample.pdf",
      xlsx_binary: "xlsx-binary"
    )

    runner = Object.new
    runner.define_singleton_method(:call) { result }

    with_stubbed_runner(runner) do
      ProcessExtractionJob.perform_now(extraction.id, password: nil)
    end

    extraction.reload

    assert extraction.completed?
    assert_equal ["Date", "Description"], extraction.columns
    assert_equal 1, extraction.transaction_count
    assert extraction.result_xlsx.attached?
  end

  test "moves extraction to password required when backend requests it" do
    extraction = build_extraction
    error = PythonExtractorRunner::PasswordRequiredError.new(
      "The uploaded PDF is password protected. Provide a valid password and retry.",
      error_code: "password_required"
    )

    runner = Object.new
    runner.define_singleton_method(:call) { raise error }

    with_stubbed_runner(runner) do
      ProcessExtractionJob.perform_now(extraction.id, password: nil)
    end

    extraction.reload

    assert extraction.password_required?
    assert_match "password protected", extraction.error_message
  end

  private

  def build_extraction
    extraction = users(:alice).extractions.create!(
      original_filename: "sample.pdf",
      status: :queued
    )
    extraction.source_pdf.attach(
      io: StringIO.new("%PDF-1.4 sample"),
      filename: "sample.pdf",
      content_type: "application/pdf"
    )
    extraction
  end

  def with_stubbed_runner(runner)
    singleton = class << PythonExtractorRunner; self; end
    original_new = PythonExtractorRunner.method(:new)

    singleton.send(:define_method, :new) do |*args, **kwargs|
      runner
    end

    yield
  ensure
    singleton.send(:define_method, :new, original_new)
  end
end
