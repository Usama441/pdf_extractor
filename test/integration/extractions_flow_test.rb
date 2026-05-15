require "test_helper"

class ExtractionsFlowTest < ActionDispatch::IntegrationTest
  test "guest uploads a pdf and queues extraction without logging in" do
    assert_enqueued_with(job: ProcessExtractionJob) do
      assert_difference("Extraction.count", 1) do
        post extractions_path, params: {
          extraction: {
            source_pdf: fixture_file_upload("sample.pdf", "application/pdf"),
            password: ""
          }
        }
      end
    end

    extraction = Extraction.order(:created_at).last

    assert_nil extraction.user_id
    assert_predicate extraction.guest_token, :present?
    assert_redirected_to extraction_path(extraction)

    follow_redirect!
    assert_match "Extraction in progress", response.body
  end

  test "user uploads a pdf and queues extraction" do
    sign_in_as(users(:alice))

    assert_enqueued_with(job: ProcessExtractionJob) do
      assert_difference("Extraction.count", 1) do
        post extractions_path, params: {
          extraction: {
            source_pdf: fixture_file_upload("sample.pdf", "application/pdf"),
            password: ""
          }
        }
      end
    end

    extraction = Extraction.order(:created_at).last
    assert_redirected_to extraction_path(extraction)

    follow_redirect!
    assert_match "Extraction in progress", response.body
  end

  test "password retry requeues the extraction" do
    sign_in_as(users(:alice))
    extraction = extractions(:password_retry)

    assert_enqueued_with(job: ProcessExtractionJob) do
      patch password_extraction_path(extraction), params: {
        extraction: { password: "secret123" }
      }
    end

    extraction.reload
    assert extraction.queued?
    assert_redirected_to extraction_path(extraction)
  end

  test "completed extraction can be downloaded" do
    sign_in_as(users(:alice))
    extraction = extractions(:completed_one)
    extraction.result_xlsx.attach(
      io: StringIO.new("xlsx"),
      filename: "statement.xlsx",
      content_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    get download_extraction_path(extraction)

    assert_response :redirect
    assert_match "/rails/active_storage/", response.headers["Location"]
  end
end
