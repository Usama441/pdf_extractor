require "json"
require "open3"
require "tmpdir"

class PythonExtractorRunner
  Result = Struct.new(:columns, :rows, :transaction_count, :source_filename, :xlsx_binary, keyword_init: true)

  class Error < StandardError
    attr_reader :error_code

    def initialize(message, error_code: nil)
      super(message)
      @error_code = error_code
    end
  end

  class PasswordRequiredError < Error; end
  class UnsupportedStatementError < Error; end

  def initialize(input_path:, password: nil)
    @input_path = input_path
    @password = password
  end

  def call
    Dir.mktmpdir("statement-flow") do |dir|
      xlsx_path = File.join(dir, "result.xlsx")
      json_path = File.join(dir, "result.json")

      stdout, stderr, status = Open3.capture3(*command(xlsx_path, json_path))
      payload = File.exist?(json_path) ? JSON.parse(File.read(json_path)) : {}

      return build_result(payload, xlsx_path) if status.success?

      message = payload["message"].presence || stderr.presence || stdout.presence || "The extractor failed."

      case status.exitstatus
      when 2
        raise PasswordRequiredError.new(message, error_code: payload["error_code"])
      when 3
        raise UnsupportedStatementError.new(message, error_code: payload["error_code"])
      else
        raise Error.new(message, error_code: payload["error_code"])
      end
    end
  end

  private

  def command(xlsx_path, json_path)
    command = [
      python_binary,
      Rails.root.join("python_backend/extractor_cli.py").to_s,
      "--input", @input_path,
      "--output-xlsx", xlsx_path,
      "--output-json", json_path
    ]

    command += [ "--password", @password ] if @password.present?
    command
  end

  def python_binary
    return ENV["PYTHON_EXTRACTOR_BIN"] if ENV["PYTHON_EXTRACTOR_BIN"].present?

    bundled_python = Rails.root.join("venv/bin/python")
    bundled_python.exist? ? bundled_python.to_s : "python3"
  end

  def build_result(payload, xlsx_path)
    Result.new(
      columns: Array(payload["columns"]),
      rows: Array(payload["rows"]),
      transaction_count: payload["transaction_count"].to_i,
      source_filename: payload["source_filename"].to_s,
      xlsx_binary: File.binread(xlsx_path)
    )
  end
end
