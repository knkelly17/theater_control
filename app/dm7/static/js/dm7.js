function getHighSchoolClass(gradYear) {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth(); // 0-indexed (0 = January, 5 = June)
  // High school typically spans 4 years before graduation
  const yearsUntilGrad = gradYear - currentYear;
  
  // Adjust if the current month is past June of their grad year (already graduated)
  if (yearsUntilGrad < 0 || (yearsUntilGrad === 0 && currentMonth >= 5)) {
    return "Graduated";
  }
  
  // Determine class based on remaining years
  switch (yearsUntilGrad) {
    case 0:
      return "Senior";
    case 1:
      return "Junior";
    case 2:
      return "Sophomore";
    case 3:
      return "Freshman";
    default:
      return gradYear > currentYear ? "Not yet in High School" : "Graduated";
  }
}