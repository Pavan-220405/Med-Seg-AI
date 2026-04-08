from fastapi import APIRouter, status, Depends, Path
from asyncpg import Connection
from uuid import UUID


from app.auth.dependencies import get_conn, RoleChecker, access_token_bearer
from app.ML_models.schemas import ModelCreate, ModelResponse, ModelBase
from app.ML_models.crud import crud_create_model, crud_delete_model


models_router = APIRouter()
admin_checker = RoleChecker(["admin"])



@models_router.post("/",dependencies=[Depends(admin_checker)],status_code=status.HTTP_201_CREATED,response_model=ModelResponse)
async def add_model(model_input : ModelBase, conn : Connection = Depends(get_conn), token_details : dict = Depends(access_token_bearer)):
    model_details = ModelCreate(**model_input.dict(), added_by=UUID(token_details['id']))
    return await crud_create_model(
        conn = conn,
        model_details = model_details
    )


@models_router.delete("/{model_id}",dependencies=[Depends(admin_checker)],response_model=ModelResponse)
async def delete_model(model_id : UUID = Path(description="UUID of the model"),conn : Connection = Depends(get_conn)):
    return await crud_delete_model(id=model_id,conn=conn)