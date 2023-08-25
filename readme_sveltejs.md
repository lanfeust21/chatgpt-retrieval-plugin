data/sveltejs/site-kit/packages/site-kit
data/sveltejs/sites/sites/hn.svelte.dev
data/sveltejs/kit/documentation/docs
data/sveltejs/svelte/documentation



This will add the dependencies to your pyproject.toml file and install them in a virtual environment managed by poetry.
poetry add beautifulsoup4 markdownify requests tqdm

Place the script:

If you've initialized a new project, you can place the script in the main directory or inside the created package directory.

Run the script:

Use poetry to run the script:

bash

poetry run python process_data_into_pinecone.py
Setting Environment Variables:

If you want to set the BEARER_TOKEN as an environment variable, you can use poetry's env command to find the path to the virtual environment and then activate it:

bash

source $(poetry env info -p)/bin/activate
Then, you can set the environment variable:

bash

export BEARER_TOKEN=your_token_value


cat .env
poetry run start

# was not recognized as plugin in the interface
deploy on digitalocean
https://orca-app-6vgyp.ondigitalocean.app/