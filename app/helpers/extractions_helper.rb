module ExtractionsHelper
  def extraction_status_label(extraction)
    extraction.status.humanize
  end

  def extraction_status_class(extraction)
    case extraction.status
    when "completed"
      "status-badge status-badge--success"
    when "failed"
      "status-badge status-badge--danger"
    when "password_required"
      "status-badge status-badge--warning"
    when "processing"
      "status-badge status-badge--active"
    else
      "status-badge status-badge--muted"
    end
  end
end
