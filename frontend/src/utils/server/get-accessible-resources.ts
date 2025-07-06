import { ResourceProps } from "@refinedev/core";
import { ROLE_RESOURCE_ACCESS } from "@types";

/**
 * Lọc resource theo role
 */
export function getAccessibleResources(resources: ResourceProps[], userRoles: string[]): ResourceProps[] {
  if (!userRoles.length) return resources;
  const allowList = ROLE_RESOURCE_ACCESS[userRoles[0]] || [];
  return resources.filter((r) => allowList.includes(r.name));
}
