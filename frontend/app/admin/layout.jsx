import AdminLayout from "@/components/admin/AdminLayout";

export const metadata = {
    title: "echo. - Admin",
    description: "echo. - Admin",
};

export default function RootAdminLayout({ children }) {

    return (
        <>
            <AdminLayout>
                {children}
            </AdminLayout>
        </>
    );
}
