class Extraction < ApplicationRecord
  belongs_to :user, optional: true

  has_one_attached :source_pdf
  has_one_attached :result_xlsx

  enum :status,
    {
      queued: "queued",
      processing: "processing",
      password_required: "password_required",
      completed: "completed",
      failed: "failed"
    },
    default: :queued,
    validate: true

  broadcasts_refreshes
  broadcasts_refreshes_to ->(extraction) { extraction.user ? [ extraction.user, :extractions ] : [ extraction.guest_token, :extractions ] }

  validates :original_filename, presence: true
  validates :guest_token, presence: true, unless: -> { user_id.present? }
  validates :transaction_count, numericality: { greater_than_or_equal_to: 0 }

  scope :recent, -> { order(created_at: :desc) }

  after_initialize :set_defaults

  def terminal?
    completed? || failed? || password_required?
  end

  private

  def set_defaults
    self.columns ||= []
    self.rows ||= []
    self.transaction_count ||= 0
    self.status ||= "queued"
  end
end
