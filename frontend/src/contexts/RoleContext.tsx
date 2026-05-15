import React, { createContext, useContext, useState } from "react";
import React, { createContext, useContext, useState, useEffect } from "react";

export type UserRole = "caregiver" | "supervisor" | "family";

interface RoleContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
  userName: string;
  userId: string;
  loading: boolean;
}

const RoleContext = createContext<RoleContextType>({
  role: "caregiver",
  setRole: () => {},
  userName: "Sarah Johnson",
  userId: "demo_user",
  loading: false,
});

export const RoleProvider = ({ children }: { children: React.ReactNode }) => {
  const [role, setRole] = useState<UserRole>("caregiver");
  const [userName, setUserName] = useState("Sarah Johnson");
  const [userId, setUserId] = useState("demo_user");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch current user from API
    const fetchCurrentUser = async () => {
      try {
        const response = await fetch("/auth/current-user");
        if (response.ok) {
          const user = await response.json();
          setRole((user.role as UserRole) || "caregiver");
          setUserName(user.name || "User");
          setUserId(user.id || "demo_user");
        }
      } catch (error) {
        console.error("Failed to fetch current user:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCurrentUser();
  }, []);

  return (
    <RoleContext.Provider value={{ role, setRole, userName, userId, loading }}>
      {children}
    </RoleContext.Provider>
  );
};

export const useRole = () => useContext(RoleContext);
