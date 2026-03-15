import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import OrgTree from '../components/OrgTree';
import api from '../api/axios';

export default function OrgTreePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/employees/org-tree')
      .then((r) => setData(r.data))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout title="Organization Tree">
      {loading ? <p>Loading...</p> : <OrgTree data={data} />}
    </Layout>
  );
}
