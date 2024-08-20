# Copyright (c) OpenMMLab. All rights reserved.
import torch_npu
from torch import Tensor


def apply_rotary_pos_emb(
    query_states: Tensor,
    key_states: Tensor,
    cos: Tensor,
    sin: Tensor,
    position_ids: Tensor,
    position_ids_1d: Tensor,
    q_embed=None,
    k_embed=None,
    context=None,
):
    bs, head, dim = query_states.shape
    numKeyValueHeads = key_states.shape[1]
    query_states = query_states.reshape(bs, head * dim)
    key_states = key_states.reshape(bs, numKeyValueHeads * dim)
    if not (hasattr(context, 'cos') or hasattr(context, 'sin')):
        cos = cos[position_ids_1d].view(1, bs, 1, -1)
        sin = sin[position_ids_1d].view(1, bs, 1, -1)
        setattr(context, 'cos', cos)
        setattr(context, 'sin', sin)

    query_states = query_states.reshape(1, bs, head, dim)
    key_states = key_states.reshape(1, bs, numKeyValueHeads, dim)
    torch_npu.npu_apply_rotary_pos_emb(query_states, key_states, context.cos,
                                       context.sin)

    return query_states.view(bs, head,
                             dim), key_states.view(bs, numKeyValueHeads, dim)
