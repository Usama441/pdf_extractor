class CreateExtractions < ActiveRecord::Migration[8.1]
  def change
    create_table :extractions do |t|
      t.references :user, null: false, foreign_key: true
      t.string :status, null: false, default: "queued"
      t.string :original_filename, null: false
      t.text :error_message
      t.jsonb :columns, null: false, default: []
      t.jsonb :rows, null: false, default: []
      t.integer :transaction_count, null: false, default: 0

      t.timestamps
    end

    add_index :extractions, [ :user_id, :created_at ]
  end
end
