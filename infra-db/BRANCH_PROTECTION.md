# Branch protection e ambientes

Após criar o repositório no GitHub:

1. Settings → Branches → Add rule para `main` e `homolog`:
   - Require a pull request before merging
   - Require status checks (job `test` / `validate`)
   - Do not allow force pushes
2. Settings → Environments: criar `homolog` e `prod` com secrets específicos.
3. Configurar OIDC AWS (`AWS_ROLE_ARN`) ou access keys nos environments.

Deploys automáticos:

- push `homolog` → ambiente homologação
- push `main` → ambiente produção
