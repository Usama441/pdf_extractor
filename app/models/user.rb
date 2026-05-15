class User < ApplicationRecord
  has_secure_password

  has_many :extractions, dependent: :destroy

  normalizes :email, with: ->(value) { value.to_s.strip.downcase }

  validates :email, presence: true, uniqueness: true
  validates :password, length: { minimum: 8 }, if: -> { password.present? }
end
