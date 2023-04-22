export const formatJson = (data: any): string => {
  try {
    return JSON.stringify(data, null, 2);
  } catch (error) {
    throw error;
  }
}