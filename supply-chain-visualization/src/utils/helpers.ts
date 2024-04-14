export const generateRandomData = (): any[] => {
    const data: any[] = [];
    const numPoints = 5; // Number of data points to generate

    for (let i = 0; i < numPoints; i++) {
      const price = Math.floor(Math.random() * 100) + 1;
      const sku = `SKU${i}`;
      data.push({ SKU: sku, Price: price });
    }

    return data;
  };
