require "test_helper"

class ExtractionTest < ActiveSupport::TestCase
  test "terminal returns true for completed extraction" do
    assert extractions(:completed_one).terminal?
  end
end
