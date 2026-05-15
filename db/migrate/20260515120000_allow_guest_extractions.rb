class AllowGuestExtractions < ActiveRecord::Migration[8.1]
  def change
    change_column_null :extractions, :user_id, true
    add_column :extractions, :guest_token, :string
    add_index :extractions, [ :guest_token, :created_at ]
  end
end
