require "test_helper"

class UserTest < ActiveSupport::TestCase
  test "normalizes email before validation" do
    user = User.create!(
      email: "  MixedCase@Example.com ",
      password: "password123",
      password_confirmation: "password123"
    )

    assert_equal "mixedcase@example.com", user.email
  end
end
