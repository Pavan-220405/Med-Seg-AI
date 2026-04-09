from asyncpg import Connection, UniqueViolationError
from fastapi import HTTPException, status
from uuid import UUID

from app.ML_models.schemas import ModelCreate, PredictionCreate


# __________________CRUD Operations for ML Models__________________________________________________________________
async def crud_create_model(model_details : ModelCreate, conn : Connection):
    query = """
        INSERT INTO models (model_name, version, description, framework, model_type, model_path,added_by)
        VALUES ($1,$2,$3,$4,$5,$6,$7)
        RETURNING *
    """
    try:
        row = await conn.fetchrow(
            query,
            model_details.model_name,
            model_details.version,
            model_details.description,
            model_details.framework,
            model_details.model_type,
            model_details.model_path,
            model_details.added_by
        )
        return dict(row) if row else None
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model already exists")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


async def crud_delete_model(id : UUID, conn : Connection):
    query = """
        DELETE FROM models
        WHERE id = $1
        RETURNING *
    """
    try:
        row = await conn.fetchrow(
            query,
            id
        )
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
        return dict(row) if row else None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    




# __________________CRUD Operations for Predictions__________________________________________________________________
async def crud_create_prediction(prediction_details : PredictionCreate, conn : Connection):
    query = """
            INSERT INTO predictions(prediction_id, user_id, model_id, input_path, mask_path,inference_time)
            VALUES ($1,$2,$3,$4,$5,$6)
            RETURNING *
        """
    
    try: 
        row = await conn.fetchrow(
            query,
            prediction_details.prediction_id,
            prediction_details.user_id,
            prediction_details.model_id,
            prediction_details.input_path,
            prediction_details.mask_path,
            prediction_details.inference_time
        )
        return dict(row) if row else None
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prediction already exists")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))