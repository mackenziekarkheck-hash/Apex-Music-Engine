"""
Project Manager - File-based song project management.

Each song project is a self-contained directory with:
- config.json: Project settings (genre, BPM, tags)
- seed.txt: Original creative brief/inspiration
- iterations/: Versioned lyrics with scoring
- approved/: Final approved lyrics and API payload
- output/: Generated audio files

Reference: Neo-Apex Architecture Documentation
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

PROJECTS_DIR = Path("projects")


class ProjectManager:
    """Manages song project directories and files."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or PROJECTS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project(
        self,
        name: str,
        genre: str = "trap",
        bpm: int = 140,
        tags: Optional[List[str]] = None,
        seed_text: str = "",
        mood: str = "aggressive",
        prompt_strength: float = 2.0,
        balance_strength: float = 0.7
    ) -> Dict[str, Any]:
        """
        Create a new song project with directory structure.
        
        Returns:
            Project config dict with id and paths
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in name.lower())
        project_id = f"{timestamp}_{safe_name}"
        
        project_path = self.base_dir / project_id
        
        (project_path / "iterations").mkdir(parents=True)
        (project_path / "approved").mkdir(parents=True)
        (project_path / "output").mkdir(parents=True)
        
        config = {
            "id": project_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "genre": genre,
            "bpm": bpm,
            "tags": tags or [genre, "hip hop", "rap"],
            "mood": mood,
            "prompt_strength": prompt_strength,
            "balance_strength": balance_strength,
            "current_iteration": 0,
            "status": "draft",
            "approved_version": None
        }
        
        self._save_json(project_path / "config.json", config)
        
        if seed_text:
            (project_path / "seed.txt").write_text(seed_text)
        
        logger.info(f"Created project: {project_id}")
        return config
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with their configs."""
        projects = []
        
        if not self.base_dir.exists():
            return projects
        
        for item in sorted(self.base_dir.iterdir(), reverse=True):
            if item.is_dir():
                config_path = item / "config.json"
                if config_path.exists():
                    try:
                        config = self._load_json(config_path)
                        config["path"] = str(item)
                        projects.append(config)
                    except Exception as e:
                        logger.warning(f"Failed to load project {item}: {e}")
        
        return projects
    
    def load_project(self, project_id: str) -> Dict[str, Any]:
        """Load a project by ID."""
        project_path = self.base_dir / project_id
        
        if not project_path.exists():
            raise ValueError(f"Project not found: {project_id}")
        
        config = self._load_json(project_path / "config.json")
        config["path"] = str(project_path)
        
        seed_path = project_path / "seed.txt"
        if seed_path.exists():
            config["seed_text"] = seed_path.read_text()
        else:
            config["seed_text"] = ""
        
        config["iterations"] = self._load_iterations(project_path)
        
        approved_path = project_path / "approved"
        if (approved_path / "final_lyrics.txt").exists():
            config["approved_lyrics"] = (approved_path / "final_lyrics.txt").read_text()
        if (approved_path / "api_payload.json").exists():
            config["approved_payload"] = self._load_json(approved_path / "api_payload.json")
        
        output_path = project_path / "output"
        config["outputs"] = []
        for audio_file in output_path.glob("*.wav"):
            config["outputs"].append({
                "filename": audio_file.name,
                "path": str(audio_file),
                "created_at": datetime.fromtimestamp(audio_file.stat().st_mtime).isoformat()
            })
        
        return config
    
    def save_seed(self, project_id: str, seed_text: str) -> None:
        """Save the seed/creative brief for a project."""
        project_path = self.base_dir / project_id
        (project_path / "seed.txt").write_text(seed_text)
        self._update_timestamp(project_id)
    
    def save_iteration(
        self,
        project_id: str,
        lyrics: str,
        scores: Dict[str, Any],
        gpt4o_response: Optional[Dict[str, Any]] = None,
        notes: str = ""
    ) -> int:
        """
        Save a new iteration of lyrics with scoring.
        
        Returns:
            Iteration version number
        """
        project_path = self.base_dir / project_id
        config = self._load_json(project_path / "config.json")
        
        version = config.get("current_iteration", 0) + 1
        iteration_dir = project_path / "iterations" / f"v{version}"
        iteration_dir.mkdir(parents=True, exist_ok=True)
        
        (iteration_dir / "lyrics.txt").write_text(lyrics)
        
        self._save_json(iteration_dir / "scoring.json", {
            "version": version,
            "created_at": datetime.now().isoformat(),
            "scores": scores,
            "notes": notes
        })
        
        if gpt4o_response:
            self._save_json(iteration_dir / "gpt4o_response.json", gpt4o_response)
        
        config["current_iteration"] = version
        config["updated_at"] = datetime.now().isoformat()
        self._save_json(project_path / "config.json", config)
        
        logger.info(f"Saved iteration v{version} for project {project_id}")
        return version
    
    def approve_iteration(
        self,
        project_id: str,
        version: int,
        api_payload: Dict[str, Any]
    ) -> None:
        """Approve an iteration and save to approved/ folder."""
        project_path = self.base_dir / project_id
        iteration_dir = project_path / "iterations" / f"v{version}"
        approved_dir = project_path / "approved"
        
        if not iteration_dir.exists():
            raise ValueError(f"Iteration v{version} not found")
        
        lyrics = (iteration_dir / "lyrics.txt").read_text()
        (approved_dir / "final_lyrics.txt").write_text(lyrics)
        
        self._save_json(approved_dir / "api_payload.json", {
            "approved_at": datetime.now().isoformat(),
            "from_version": version,
            "payload": api_payload
        })
        
        if (iteration_dir / "scoring.json").exists():
            shutil.copy(iteration_dir / "scoring.json", approved_dir / "final_scoring.json")
        
        config = self._load_json(project_path / "config.json")
        config["status"] = "approved"
        config["approved_version"] = version
        config["updated_at"] = datetime.now().isoformat()
        self._save_json(project_path / "config.json", config)
        
        logger.info(f"Approved v{version} for project {project_id}")
    
    def save_output(
        self,
        project_id: str,
        audio_path: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save generated audio to project output folder.
        
        Returns:
            Path to saved audio file
        """
        project_path = self.base_dir / project_id
        output_dir = project_path / "output"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_filename = f"song_{timestamp}.wav"
        dest_path = output_dir / dest_filename
        
        if os.path.exists(audio_path):
            shutil.copy(audio_path, dest_path)
        
        self._save_json(output_dir / f"song_{timestamp}_meta.json", {
            "generated_at": datetime.now().isoformat(),
            "source_path": audio_path,
            **metadata
        })
        
        config = self._load_json(project_path / "config.json")
        config["status"] = "completed"
        config["updated_at"] = datetime.now().isoformat()
        self._save_json(project_path / "config.json", config)
        
        logger.info(f"Saved output to {dest_path}")
        return str(dest_path)
    
    def update_config(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update project configuration."""
        project_path = self.base_dir / project_id
        config = self._load_json(project_path / "config.json")
        
        for key, value in updates.items():
            if key not in ["id", "created_at", "path"]:
                config[key] = value
        
        config["updated_at"] = datetime.now().isoformat()
        self._save_json(project_path / "config.json", config)
        
        return config
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its files."""
        project_path = self.base_dir / project_id
        
        if project_path.exists():
            shutil.rmtree(project_path)
            logger.info(f"Deleted project: {project_id}")
            return True
        return False
    
    def _load_iterations(self, project_path: Path) -> List[Dict[str, Any]]:
        """Load all iterations for a project."""
        iterations = []
        iterations_dir = project_path / "iterations"
        
        if not iterations_dir.exists():
            return iterations
        
        for item in sorted(iterations_dir.iterdir()):
            if item.is_dir() and item.name.startswith("v"):
                try:
                    version = int(item.name[1:])
                    iteration = {"version": version}
                    
                    lyrics_path = item / "lyrics.txt"
                    if lyrics_path.exists():
                        iteration["lyrics"] = lyrics_path.read_text()
                    
                    scoring_path = item / "scoring.json"
                    if scoring_path.exists():
                        scoring = self._load_json(scoring_path)
                        iteration["scores"] = scoring.get("scores", {})
                        iteration["created_at"] = scoring.get("created_at")
                        iteration["notes"] = scoring.get("notes", "")
                    
                    iterations.append(iteration)
                except Exception as e:
                    logger.warning(f"Failed to load iteration {item}: {e}")
        
        return sorted(iterations, key=lambda x: x["version"])
    
    def _update_timestamp(self, project_id: str) -> None:
        """Update the updated_at timestamp."""
        project_path = self.base_dir / project_id
        config = self._load_json(project_path / "config.json")
        config["updated_at"] = datetime.now().isoformat()
        self._save_json(project_path / "config.json", config)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Save JSON file with pretty formatting."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
