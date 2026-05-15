class ApplicationController < ActionController::Base
  # Only allow modern browsers supporting webp images, web push, badges, import maps, CSS nesting, and CSS :has.
  allow_browser versions: :modern

  # Changes to the importmap will invalidate the etag for HTML responses
  stale_when_importmap_changes

  helper_method :current_user, :signed_in?, :guest_token

  private

  def current_user
    @current_user ||= User.find_by(id: session[:user_id])
  end

  def signed_in?
    current_user.present?
  end

  def require_login
    return if signed_in?

    redirect_to login_path, alert: "Please sign in to continue."
  end

  def guest_token
    session[:guest_token] ||= SecureRandom.uuid
  end

  def redirect_if_authenticated
    return unless signed_in?

    redirect_to dashboard_path, notice: "You are already signed in."
  end
end
