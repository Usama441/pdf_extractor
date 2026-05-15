require "test_helper"

class AuthenticationFlowTest < ActionDispatch::IntegrationTest
  test "user can sign up, log out, and sign back in" do
    get signup_path
    assert_response :success

    assert_difference("User.count", 1) do
      post signup_path, params: {
        user: {
          email: "new-user@example.com",
          password: "password123",
          password_confirmation: "password123"
        }
      }
    end

    assert_redirected_to dashboard_path
    follow_redirect!
    assert_response :success
    assert_match "Extract bank statement PDFs", response.body

    delete logout_path
    assert_redirected_to login_path

    post login_path, params: { email: "new-user@example.com", password: "password123" }
    assert_redirected_to dashboard_path
  end
end
