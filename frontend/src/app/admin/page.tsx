'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Admin, Resource, List, Datagrid, TextField, Edit, SimpleForm, TextInput, Create, NumberField, NumberInput, UrlField, ImageField } from 'react-admin';
import { useAuth } from '@/contexts/AuthContext';
import dataProvider from '@/lib/dataProvider';
import { DateField } from 'react-admin';
import theme from '@/lib/theme';
import MyLayout from '@/lib/MyLayout';




const UserList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="username" />
      <TextField source="email" />
    </Datagrid>
  </List>
);

const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="username" />
      <TextInput source="email" />
      <TextInput source="password" type="password" />
    </SimpleForm>
  </Edit>
);

const UserCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="username" />
      <TextInput source="email" />
      <TextInput source="password" type="password" />
    </SimpleForm>
  </Create>
);


const SpaceList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <ImageField source="image" />
    </Datagrid>
  </List>
);

const SpaceEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" />
      <TextInput source="image" />
    </SimpleForm>
  </Edit>
);

const SpaceCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" />
      <TextInput source="image" />
    </SimpleForm>
  </Create>
);


const ProductList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <NumberField source="price" />
      <UrlField source="purchase_link" />
      <ImageField source="image_url" />
      <TextField source="category" />
    </Datagrid>
  </List>
);

const ProductEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" />
      <NumberInput source="price" />
      <TextInput source="purchase_link" />
      <TextInput source="image_url" />
      <TextInput source="category" />
    </SimpleForm>
  </Edit>
);

const ProductCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" />
      <NumberInput source="price" />
      <TextInput source="purchase_link" />
      <TextInput source="image_url" />
      <TextInput source="category" />
    </SimpleForm>
  </Create>
);


const StyleList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <ImageField source="image" />
    </Datagrid>
  </List>
);

const StyleEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" />
      <TextInput source="image" />
    </SimpleForm>
  </Edit>
);

const StyleCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" />
      <TextInput source="image" />
    </SimpleForm>
  </Create>
);

const UserHistoryList = () => (
  <List>
    <Datagrid rowClick={false}>
      <TextField source="id" />
      <TextField source="user_id" label="User ID" />
      <TextField source="product_id" label="Product ID" />
      <TextField source="action" />
      <DateField source="timestamp" showTime />
    </Datagrid>
  </List>
);

const UserHistoryCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="user_id" />
      <TextInput source="product_id" />
      <TextInput source="action" />
    </SimpleForm>
  </Create>
);





export default function AdminPage() {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!isAuthenticated || !isAdmin)) {
      router.push('/'); 
    }
  }, [isAuthenticated, isAdmin, loading, router]);

  if (loading) return <div>Cargando...</div>;
  if (!isAuthenticated || !isAdmin) return null;

  return (
    <Admin dataProvider={dataProvider}  theme={theme} layout={MyLayout}>
      <Resource name="users" list={UserList} edit={UserEdit} create={UserCreate} />
      <Resource name="spaces" list={SpaceList} edit={SpaceEdit} create={SpaceCreate} />
      <Resource name="products" list={ProductList} edit={ProductEdit} create={ProductCreate} />
      <Resource name="styles" list={StyleList} edit={StyleEdit} create={StyleCreate} />
      <Resource
        name="user_history"
        list={UserHistoryList}
        create={UserHistoryCreate}
        options={{ label: "User History" }}
      />
    </Admin>
  );
}