// Sample business logic code - we expect to have a full address in the "address" string, e.g. "2 Park St, Sydney, NSW 2000, Australia"
export const isAddressValid = (event) => {
  if (!event || !event.address) return false;

  const addressWords = event.address.split(',');
  if (addressWords.length != 4) return false;

  return true;
};
