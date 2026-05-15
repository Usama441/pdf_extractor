class DashboardController < ApplicationController
  def show
    @extraction = Extraction.new
    @extractions = signed_in? ? current_user.extractions.recent : Extraction.none
  end
end
