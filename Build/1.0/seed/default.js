const toEntries = (labels) =>
  labels.map((label) => ({
    label,
    value: label
      .toLowerCase()
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
  }));

// Source: Design/Treesa.jpeg (Treesa Agencies Transaction Head)
export const treesa = toEntries([
  "Treesa - SIB",
  "PD - IndusInd",
  "Salary",
  "Salary Advance",
  "Weekly Allowance",
  "Cash at Cochin",
  "Triprayar - CNG",
  "Triprayar - Petrol",
  "Triprayar - Diesel",
  "Triprayar - Driver",
  "Ponnani - CNG",
  "Ponnani - Petrol",
  "Ponnani - Diesel",
  "Ponnani - Driver",
  "Pattambi - CNG",
  "Pattambi - Petrol",
  "Pattambi - Diesel",
  "Pattambi - Driver",
  "EKM - CNG",
  "EKM - Petrol",
  "EKM - Diesel",
  "EKM - Driver",
  "KSFE Kuri",
  "Sadhu Kuri",
  "Stationary",
  "Cash or Chq John P.C",
  "Office Expense",
  "ICE - TCR",
  "ICE - Manjeri",
  "Fast Tag",
  "Repairs of Workshop",
  "Showroom Expenses",
  "CNG - Thrissur",
  "Vehicle Permit",
  "Plant",
  "Manjeri Diesel",
  "Manjeri CNG",
  "Plant Diesel",
  "Advertisement",
  "Tax",
  "Electrical Expense",
  "Rent",
  "Computer Maintenance",
  "Internet Charge",
  "Mobile Charge",
  "Parking Charge",
  "GST & Tax",
  "Vehicle EMIs"
]);

// Source: Design/Daily.jpeg (Daily Collection)
export const daily = toEntries([
  "TPR Collection - Akhil Babu",
  "Ponnani Collection - Sanju",
  "Pattambi Collection - Devadas",
  "Lenin",
  "Mohandas",
  "Vivek",
  "Jeeva Farms",
  "Cochin Freshway",
  "RAK",
  "Daily Route Jilshad",
  "Daily Route Rajeev",
  "Daily Route Praveen",
  "Daily Route Mahesh",
  "Daily Route Mathew",
  "Daily Route Sumesh",
  "John P.C",
  "Cochin 11 - Shaji PBVR",
  "Cochin 11 - Shaji BVR",
  "Anil Chegannur",
  "Direct Route Emmanuvel, Cochin",
  "Shiji - Kodungallur",
  "Direct Route Salam, Cochin"
]);

const dropdownListEntries = { treesa, daily };

export default dropdownListEntries;
