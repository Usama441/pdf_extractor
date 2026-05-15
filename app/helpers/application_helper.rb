module ApplicationHelper
  def supported_bank_logos
    [
      { name: "ADCB", file: "banks_logo/Abu_Dhabi_Commercial_Bank_logo.svg.png", size: "wide" },
      { name: "Mashreq", file: "banks_logo/Mashreq-Bank-Logo-Vector.svg-.png", size: "wide" },
      { name: "Revolut", file: "banks_logo/REVOLUT-removebg-preview.png", size: "compact" },
      { name: "Wio", file: "banks_logo/WIO.png", size: "compact" },
      { name: "Emirates NBD", file: "banks_logo/lg-67a9470992e1d-Emirates-NBD.webp", size: "square" },
      { name: "Payoneer", file: "banks_logo/png-clipart-payoneer-logo-tech-companies-removebg-preview.png", size: "wide" },
      { name: "Starling", file: "banks_logo/png-clipart-starling-bank-finance-financial-services-hsbc-starling-purple-blue-removebg-preview.png", size: "wide" },
      { name: "RAKBANK", file: "banks_logo/rakbank-cover-removebg-preview.png", size: "compact" }
    ]
  end
end
