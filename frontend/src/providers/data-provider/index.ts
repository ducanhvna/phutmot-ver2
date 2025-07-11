"use client";

import { DataProvider } from "@refinedev/core";
import dataProviderSimpleRest from "@refinedev/simple-rest";

// Create the default REST data provider for your backend API
const defaultDataProvider = dataProviderSimpleRest(
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8979/"
);

// Create a specific data provider for the JSONPlaceholder API
const jsonPlaceholderProvider = dataProviderSimpleRest(
  "https://jsonplaceholder.typicode.com"
);

// Export a combined data provider that routes requests based on resource
export const dataProvider: DataProvider = {
  ...defaultDataProvider,

  // Override specific methods to route requests to the right provider
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    if (resource === "posts") {
      // Route posts requests to JSONPlaceholder
      return jsonPlaceholderProvider.getList({
        resource,
        pagination,
        filters,
        sorters,
        meta,
      });
    }

    // Default to your backend API for other resources
    return defaultDataProvider.getList({
      resource,
      pagination,
      filters,
      sorters,
      meta,
    });
  },

  getOne: async ({ resource, id, meta }) => {
    if (resource === "posts") {
      return jsonPlaceholderProvider.getOne({ resource, id, meta });
    }
    return defaultDataProvider.getOne({ resource, id, meta });
  },

  create: async ({ resource, variables, meta }) => {
    if (resource === "posts") {
      return jsonPlaceholderProvider.create({ resource, variables, meta });
    }
    return defaultDataProvider.create({ resource, variables, meta });
  },

  update: async ({ resource, id, variables, meta }) => {
    if (resource === "posts") {
      return jsonPlaceholderProvider.update({ resource, id, variables, meta });
    }
    return defaultDataProvider.update({ resource, id, variables, meta });
  },

  deleteOne: async ({ resource, id, meta }) => {
    if (resource === "posts") {
      return jsonPlaceholderProvider.deleteOne({ resource, id, meta });
    }
    return defaultDataProvider.deleteOne({ resource, id, meta });
  },

  // Other methods will use the default provider
}
