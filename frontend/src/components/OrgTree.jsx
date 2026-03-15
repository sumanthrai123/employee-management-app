import './OrgTree.css';

function TreeNode({ node }) {
  if (!node) return null;
  return (
    <div className="org-tree-node">
      <div className="node-card">
        <strong>{node.name}</strong>
        <span>{node.job_title}{node.department ? ` · ${node.department}` : ''}</span>
      </div>
      {node.children && node.children.length > 0 && (
        <div className="node-children">
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function OrgTree({ data }) {
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return <p className="card">No organization data. Add employees and set their &quot;Manager&quot; to build the tree.</p>;
  }
  const nodes = Array.isArray(data) ? data : [data];
  return (
    <div className="org-tree-root">
      {nodes.map((node) => (
        <TreeNode key={node.id} node={node} />
      ))}
    </div>
  );
}
